from flask import Flask, request
from markupsafe import escape
from src.rag.hybrid_gemini import HybridGeminiRag
from src.config import Configuration
import logging

# When call API, please check the "status" field first
# 200 is success, else is error

app = Flask(__name__)

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
    #question = "This is user input question"
    answer = "This is a sample json result"
    data = {"question": "What is life", "answer": answer, "status": 200}
    return data

@app.route("/qa", methods=["POST"])
def answer_major():
    if request.method != "POST":
        return {"status": 404}
    try:
        question = request.form.get("question")
        answer = RAG.rag.invoke(escape(question))
        #answer = "tôi không biết thông tin chi tiết"
        data = {"question": question, "answer": answer, "status": 200}
    except Exception as Argument:
        with open("rag.log", "a") as f:
            f.write(f"[ERROR] {str(Argument)}")
        return {"status": 404}
    return data

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int("5000"), debug=True)
