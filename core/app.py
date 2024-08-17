from flask import Flask, request
from src.config import Configuration
from src.service.applog import AppLogService
import os
from flask_cors import CORS
from src.rag.hg_parent_retriever import HugFaceParentParallelRAG
from src.service.provider import ProviderService
from src.utils.type_utils import get_default_config
from src.robot import RAGRobot
from datasets import load_dataset
from typing import Dict

# When call API, please check the "status" field first
# 200 is success, else is error
def get_ueh_config():
    data = {
        "DATA_REPO":"BroDeadlines/TEST.UEH.ueh_copora_data", 
        "SUBSET": "default", 
        "VEC_IDX": "vec-sentence-ueh-sentence", 
        'TXT_IDX': 'text-sentence-ueh-sentence', 
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
        self.robots: Dict[str, RAGRobot] = {}
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
        #config['llm'] = "gemini-1.0-pro"
        config['llm'] = "gemini-1.5-flash"
        return config
 
    def get_robot(self, id: str) -> HugFaceParentParallelRAG:
        if id in self.robots:
            return self.robots[id]
        self.robots[id] = HugFaceParentParallelRAG(
            provider=self.provider, config=self.config,
            text_corpora=self.dataset['train'], uni=self.UNI)
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
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    ### End Points ###
    @app.route('/')
    def hello_world():
        data = {"message": "Hello world", "status": 200}
        return data


    @app.route("/tdt_qa", methods=["POST"])
    def tdt_answer():
        return bot_answer(request=request, manager=tdt_manager)
    
    @app.route("/ueh_qa", methods=['POST'])
    def ueh_answer():
        return bot_answer(request=request, manager=ueh_manager)

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
