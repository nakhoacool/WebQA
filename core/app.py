from flask import Flask
from markupsafe import escape
from src.rag.hybrid_gemini import HybridGeminiRag
from src.config import Configuration

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

@app.route("/qa/<question>")
def answer_major(question):
    answer = RAG.rag.invoke(escape(question))
    data = {"question": question, "answer": answer, "status": 200}
    return data

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int("5000"), debug=True)