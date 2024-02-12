from flask import Flask, request
from markupsafe import escape
from src.config import Configuration
from langsmith.run_helpers import traceable
from src.userbot import UserBot
from src.masterbot import MasterBot
import os
from flask_cors import CORS

# When call API, please check the "status" field first
# 200 is success, else is error

master = MasterBot()
user_bots = {"u12": UserBot("u12", masterRef=master)}

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    # enable CORS
    CORS(app=app)
    config = Configuration()
    config.enable_tracing("LEARN")
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        with open("./rag.log", "a") as f:
            f.write('ERROR: cannot make dir '+app.instance_path)
    
    ### End Points ###
    @app.route('/')
    def hello_world():
        data = {"message": "Hello world", "status": 200}
        return data

    @app.route("/test_qa/")
    def test_answer_major():
        answer = ""
        with open("./core/sample.txt") as f:
            answer = "".join(f.readlines()) 
        data = {"question": "What is life", "answer": answer, "status": 200}
        return data

    @app.route("/qa", methods=["POST"])
    @traceable(tags=["rag_live", "major"])
    def answer_major():
        """
            Ask RAG major blog post Service.
            This service can be called to answer any question related to "major"
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
            userid = "u12"
            bot = user_bots[userid]
            rag_resp = bot.ask(question=escape(question))
            data = {
                "question": question, 
                "answer": rag_resp.answer,
                "category": rag_resp.category, 
                "status": 200, 
                "notfound": rag_resp.is_notfound()}
        except Exception as Argument:
            with open("rag.log", "a") as f:
                f.write(f"[ERROR] {str(Argument)}")
            return {"status": 404}
        return data
    
    return app

if __name__ == '__main__':
    create_app().run(host="0.0.0.0", port=int("5000"), debug=True)