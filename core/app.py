from flask import Flask, request
from markupsafe import escape
from src.config import Configuration
from src.service.applog import AppLogService
from langsmith.run_helpers import traceable
import os
from src.rag.hybrid_rank_rag import HybridRFFGeminiRAG
from flask_cors import CORS
from src.service.provider import ProviderService

# When call API, please check the "status" field first
# 200 is success, else is error


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    # enable CORS
    CORS(app=app)
    log_service = AppLogService(name="app.log")
    config = Configuration()
    config.enable_tracing("PARA_BOT_DEMO")
    app_provider = ProviderService()
    app_config = app_provider.categories.full_data
    RAG_BOT = HybridRFFGeminiRAG(provider=app_provider, rag_config=app_config, update_notification_func=None)

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
        log_service.logger.error(msg='ERROR: cannot make dir '+app.instance_path)
    
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
            rag_resp = RAG_BOT.ask_rag(question.strip())
            data = {
                "question": question, 
                "answer": rag_resp.answer,
                "category": rag_resp.category, 
                "status": 200, 
                "notfound": rag_resp.is_notfound()}
        except Exception as Argument:
            log_service.logger.exception(msg="[APP] answer_major went wrong!")
            return {"status": 404}
        return data
    
    return app

if __name__ == '__main__':
    create_app().run(host="0.0.0.0", port=int("5001"), debug=True)
