import jwt
from flask import Flask, request, jsonify
from functools import wraps
from src.config import Configuration
from src.service.applog import AppLogService
from flask_cors import CORS
from src.rag.hg_parent_retriever import HugFaceParentParallelRAG
from src.rag.hyde_rag import HydeHybridSearchRAG
from src.service.provider import ProviderService
from src.utils.type_utils import get_default_config
from datasets import load_dataset
from typing import Dict

def get_ueh_config():
    data = {
        "DATA_REPO":"BroDeadlines/TEST.UEH.ueh_copora_data", 
        "SUBSET": "default", 
        "VEC_IDX": "vec-sentence-ueh-unique", 
        'TXT_IDX': 'text-sentence-ueh-unique', 
        "UNI": "Kinh tế TP. Hồ Chí Minh"}
    return data

def get_RAPTOR_ueh_config():
    data = {
        "DATA_REPO": '',
        "SUBSET": "", 
        "VEC_IDX": "vec-raptor-ueh-data-tree-unique", 
        'TXT_IDX': 'text-raptor-ueh-data-tree-unique', 
        "UNI": "Kinh tế TP. Hồ Chí Minh"}
    return data

def get_tdt_config():
    data = {
        "DATA_REPO":"BroDeadlines/TEST.TDT.mini.tdt_copora_data",
        "SUBSET": "compact", 
        "VEC_IDX": "vec-sentence-compact-tdt-sentence", 
        'TXT_IDX': 'text-sentence-compact-tdt-sentence', 
        "UNI": "Tôn Đức Thắng"}
    return data

def get_RAPTOR_tdt_config():
    data = {
        "DATA_REPO":"",
        "SUBSET": "", 
        "VEC_IDX": "vec-raptor-medium_index_tdt_vi", 
        'TXT_IDX': 'text-raptor-medium_index_tdt_vi', 
        "UNI": "Tôn Đức Thắng"}
    return data

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        config = Configuration()
        SECRET_KEY = config.load_jwt_secret()
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token is expired!'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 403
        return f(*args, **kwargs)
    return decorated

class RobotManager:
    """
        This class is designed to manage multiple robots for multiple users.
        Simply put, it get the correct robot that serving for a particular user.
    """
    def __init__(self, robotconfig) -> None:
        DATA_REPO = robotconfig['DATA_REPO']
        SUBSET = robotconfig['SUBSET']
        self.VEC_IDX = robotconfig['VEC_IDX']
        self.TXT_IDX = robotconfig['TXT_IDX']
        self.UNI = robotconfig['UNI']
        # end config
        self.robots: Dict[str, HugFaceParentParallelRAG] = {}
        self.provider = ProviderService()
        if len(SUBSET) > 0:
            self.dataset = load_dataset(DATA_REPO, SUBSET)
        else:
            self.dataset = load_dataset(DATA_REPO)
        self.config = self.create_proposition_config()
        print(f"===> Load copora data complete: \n{self.dataset}")
        return

    def create_proposition_config(self):
        config = get_default_config()
        config['vec_index'] = self.VEC_IDX
        config['txt_index'] = self.TXT_IDX
        config['total_k'] = 8
        config['llm'] = "gemini-1.0-pro"
        # config['llm'] = "gemini-1.5-flash"
        return config
 
    def get_robot(self, id: str) -> HugFaceParentParallelRAG:
        if id in self.robots:
            return self.robots[id]
        self.robots[id] = HugFaceParentParallelRAG(
            provider=self.provider, config=self.config,
            text_corpora=self.dataset['train'], uni=self.UNI)
        return self.robots[id]
    
class RobotManagerRAPTOR(RobotManager):

    def __init__(self, robotconfig) -> None:
        self.VEC_IDX = robotconfig['VEC_IDX']
        self.TXT_IDX = robotconfig['TXT_IDX']
        self.UNI = robotconfig['UNI']
        # end config
        self.robots: Dict[str, HydeHybridSearchRAG] = {}
        self.provider = ProviderService()
        self.config = self.create_proposition_config()
        return
    
    def get_robot(self, id: str) -> HydeHybridSearchRAG:
        if id in self.robots:
            return self.robots[id]
        self.robots[id] = HydeHybridSearchRAG(
            provider=self.provider, config=self.config, uni=self.UNI)
        return self.robots[id]


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    # enable CORS
    CORS(app=app)
    log_service = AppLogService(name="app.log")
    config = Configuration()
    config.enable_tracing("DEMO")
    tdt_manager = RobotManager(robotconfig=get_tdt_config())
    ueh_manager = RobotManager(robotconfig=get_ueh_config())
    tdt_raptor_manager = RobotManagerRAPTOR(robotconfig=get_RAPTOR_tdt_config())
    ueh_raptor_manager = RobotManagerRAPTOR(robotconfig=get_RAPTOR_ueh_config())
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    ### End Points ###
    @app.route("/tdt_qa", methods=["POST"])
    @token_required
    def tdt_answer():
        return bot_answer(request=request, manager=tdt_manager)
    
    @app.route("/ueh_qa", methods=['POST'])
    @token_required
    def ueh_answer():
        return bot_answer(request=request, manager=ueh_manager)
    
    @app.route("/raptor_ueh_qa", methods=['POST'])
    @token_required
    def ueh_raptor_answer():
        return bot_answer(request=request, manager=ueh_raptor_manager)
    

    @app.route("/raptor_tdt_qa", methods=['POST'])
    @token_required
    def tdt_raptor_answer():
        return bot_answer(request=request, manager=tdt_raptor_manager)

    def bot_answer(request, manager):
        """
            Ask RAG major blog post Service.
            @param question
            @param user personal id
            
            @return {
                question: the input question,
                answer: the answer from RAG,
                notfound: is the question answerable,
                status: API request status, 
            } 
        """
        if request.method != "POST":
            return {"status": 404}
        try:
            question = request.form.get("question")
            userid = request.form.get("userid")

            token = request.headers['Authorization'].split(" ")[1]
            config = Configuration()
            SECRET_KEY = config.load_jwt_secret()

            access_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            token_id = access_token.get('id')

            if token_id != userid:
                return jsonify({'message': 'User ID does not match token ID!'}), 403

            bot = manager.get_robot(id=userid)
            rag_resp = bot.answer(question.strip())
            data = {
                "question": question, 
                "answer": rag_resp["answer"],
                "exec_time": rag_resp['exc_second'],
                "status": 200
                }
        except Exception as Argument:
            log_service.logger.exception(msg="[APP] answer_major went wrong!")
            return {"status": 404}
        return data
    
    return app

if __name__ == '__main__':
    create_app().run(host="0.0.0.0", port=int("5000"))
