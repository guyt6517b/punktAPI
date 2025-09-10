# app.py
from flask import Flask, request, jsonify
import nltk

# Download punkt once (this will stay on the server)
nltk.download('punkt')

from nltk.tokenize import word_tokenize, sent_tokenize

app = Flask(__name__)

@app.route("/tokenize", methods=["POST"])
def tokenize():
    data = request.get_json()
    text = data.get("text", "")
    sentences = sent_tokenize(text)
    words = [word_tokenize(s) for s in sentences]
    return jsonify({"sentences": sentences, "words": words})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
