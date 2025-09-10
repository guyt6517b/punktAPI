from flask import Flask, request, jsonify
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

# Ensure punkt is present
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)

app = Flask(__name__)

@app.route("/")
def home():
    return {"status": "running"}

@app.route("/ping")
def ping():
    return {"status": "ok"}

@app.route("/tokenize", methods=["POST"])
def tokenize():
    data = request.get_json(force=True) or {}
    text = data.get("text", "")
    sentences = sent_tokenize(text)
    words = [word_tokenize(s) for s in sentences]
    return jsonify({"sentences": sentences, "words": words})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
