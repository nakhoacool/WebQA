from flask import Flask, request
from markupsafe import escape
from src.rag.hybrid_gemini import HybridGeminiRag
from src.config import Configuration
import logging
from flask_cors import CORS

# When call API, please check the "status" field first
# 200 is success, else is error

app = Flask(__name__)
# enable CORS
CORS(app=app)

config = Configuration()
config.enable_tracing("TEST")

WELCOME = "Hello User"

RAG = HybridGeminiRag(
    es_index="labse-major",
    embed_model="sentence-transformers/LaBSE", config=config)

@app.route('/')
def hello_world():
    data = {"message": WELCOME, "status": 200}
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
        rag_resp = RAG.ask_rag(question=escape(question))
        data = {
            "question": question, 
            "answer": rag_resp.answer, 
            "status": 200, 
            "notfound": rag_resp.is_notfound()}
    except Exception as Argument:
        with open("rag.log", "a") as f:
            f.write(f"[ERROR] {str(Argument)}")
        return {"status": 404}
    return data

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int("5000"), debug=True)
