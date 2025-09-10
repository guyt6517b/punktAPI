from flask import Flask, request, jsonify
import random
import re
from collections import defaultdict, deque
from difflib import SequenceMatcher

app = Flask(__name__)

# --- Shrek corpus ---
shrek_quotes = [
    "Better out than in, I always say.",
    "This is the part where you run away.",
    "Ogres are like onions.",
    "What are you doing in my swamp?",
    "Donkey, you're gonna be fine.",
    "Some of you may die, but it's a sacrifice I am willing to make.",
    "Donkey! Can I stay with you?",
    "You were the first person I ever kissed… and I want you to be the last.",
    "Do you know the muffin man?",
    "Somebody once told me the world is gonna roll me… wait wrong movie, but still.",
    "That'll do, Donkey. That'll do."
]

mask = {
    "swamp": ["place", "environment", "area"],
    "donkey": ["friend", "companion", "buddy"],
    "ogres": ["people", "individuals"],
    "onions": ["layers", "complexities"],
    "the last": ["I care", "I understand ya"]
}

# --- Markov chain builder ---
def build_markov(corpus, n=2):
    chains = defaultdict(list)
    words = []
    for quote in corpus:
        words.extend(re.findall(r"[\w'…]+|[.,!?]", quote))
    queue = deque(maxlen=n)
    for w in words:
        if len(queue) == n:
            chains[tuple(queue)].append(w)
        queue.append(w)
    return chains

markov2 = build_markov(shrek_quotes, 2)
markov3 = build_markov(shrek_quotes, 3)

# --- Mask Shrek words ---
def mask_shrek(sentence, mask, chance=0.3):
    def replace_word(word):
        key = word.lower().strip(".,!?…")
        if key in mask and random.random() < chance:
            replacement = random.choice(mask[key])
            if word[0].isupper():
                replacement = replacement.capitalize()
            if word[-1] in ".,!?…":
                replacement += word[-1]
            return replacement
        return word
    return " ".join(replace_word(w) for w in sentence.split())

# --- Extract keywords ---
stop_words = {"the", "is", "a", "an", "and", "or", "but", "to", "i", "you", "it", "my", "in", "of", "on", "for"}

def extract_keywords(text):
    words = re.findall(r"\w+", text.lower())
    return [w for w in words if w.lower() not in stop_words]

# --- Generate sentence ---
def generate_sentence(chain, n=2, max_words=20, seed_words=None):
    if seed_words:
        candidates = [k for k in chain if any(w.lower() in k for w in seed_words)]
        start = random.choice(candidates) if candidates else random.choice(list(chain.keys()))
    else:
        start = random.choice(list(chain.keys()))
   
    sentence = list(start)
    for _ in range(max_words - n):
        next_words = chain.get(start)
        if not next_words:
            break
        next_word = random.choice(next_words)
        sentence.append(next_word)
        start = tuple(sentence[-n:])
        if next_word in ".!?":
            break

    text = " ".join(sentence).replace(" .", ".").replace(" ,", ",")
    return mask_shrek(text, mask)

# --- Shrekify API Endpoint ---
@app.route('/shrekify', methods=['POST'])
def shrekify():
    data = request.get_json()
    user_input = data.get("text", "")

    if not user_input:
        return jsonify({"response": "Please provide some input for therapy."})

    # Extract keywords from the user's input
    keywords = extract_keywords(user_input)
    
    # Randomly choose whether to use 2-word or 3-word Markov chain
    chain, n = (markov3, 3) if random.random() < 0.6 else (markov2, 2)
    
    # Generate Shrek-like response based on input
    response = generate_sentence(chain, n=n, max_words=20, seed_words=keywords)
    
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
