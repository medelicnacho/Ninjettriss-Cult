from flask import Flask, request, jsonify, send_from_directory
import random
import re
from pathlib import Path

app = Flask(__name__, static_folder=".", static_url_path="")

DOCTRINE_PATH = Path("doctrine.txt")


# -----------------------------
# TYPO NORMALIZATION
# -----------------------------

def normalize_typos(text: str):

    t = text.lower().strip()

    typo_map = {

        "summerize": "summarize",
        "sumerize": "summarize",
        "summrize": "summarize",
        "sumarize": "summarize",
        "sumrize": "summarize",

        "waht": "what",
        "whta": "what",
        "whwta": "what",
        "wat": "what",
        "wht": "what",

        "taht": "that",
        "thta": "that",

        "teh": "the",
        "hte": "the",

        "peiople": "people",
        "peopel": "people",
        "poeple": "people",
        "ppl": "people",

        "orcacel": "oracle",
        "oracel": "oracle",
        "orcacle": "oracle",

        "ninjetrirss": "ninjettriss",
        "ninjetriss": "ninjettriss",

        "doctirne": "doctrine",
        "docrtine": "doctrine",
        "doctine": "doctrine",

        "surcere": "sorcerer",
        "sorcere": "sorcerer",

        "ulitmat": "ultimate",
        "ulitmate": "ultimate",

        "reconize": "recognize",
        "recgonize": "recognize",

        "dsniged": "designed",
        "disniged": "designed",

        "trian": "train",
        "traning": "training",
        "trianing": "training",

        "becuase": "because",
        "becasue": "because",

        "wnat": "want",
        "iwant": "i want",

        "whats": "what is",
        "whats up": "what is up",

        "what dose": "what does",
        "what dose that mean": "what does that mean",

        "expalin": "explain",
        "explian": "explain",

        "modle": "model",
        "moddel": "model",

        "deth": "death",
        "dieing": "dying",
    }

    for wrong, right in typo_map.items():
        t = t.replace(wrong, right)

    # remove repeated letters (whhaaaat → what)
    t = re.sub(r'(.)\1{2,}', r'\1', t)

    # remove double spaces
    t = re.sub(r'\s+', ' ', t)

    return t.strip()


# -----------------------------
# LOAD DOCTRINE
# -----------------------------

def load_doctrine():
    if DOCTRINE_PATH.exists():
        return DOCTRINE_PATH.read_text(encoding="utf-8", errors="ignore")
    return ""


DOCTRINE_TEXT = load_doctrine()


# -----------------------------
# SPLIT SECTIONS
# -----------------------------

def split_sections(text):

    sections = []
    current_title = "INTRO"
    current_content = []

    for line in text.splitlines():

        stripped = line.strip()

        if stripped.isupper() and len(stripped) > 5:

            if current_content:
                sections.append({
                    "title": current_title,
                    "content": " ".join(current_content)
                })

            current_title = stripped
            current_content = []

        else:
            if stripped:
                current_content.append(stripped)

    if current_content:
        sections.append({
            "title": current_title,
            "content": " ".join(current_content)
        })

    return sections


SECTIONS = split_sections(DOCTRINE_TEXT)


# -----------------------------
# MEMORY
# -----------------------------

LAST_TOPIC = None


# -----------------------------
# SEARCH
# -----------------------------

def tokenize(text):
    text = normalize_typos(text)
    return re.findall(r"[a-zA-Z']+", text)


def score_section(query, section):

    q_tokens = tokenize(query)

    title = section["title"].lower()
    content = section["content"].lower()

    score = 0

    for token in q_tokens:

        if token in title:
            score += 8

        if token in content:
            score += 1

    if "four stage" in query or "four stages" in query:
        if "doctrine summary" in title or "tech arc" in title:
            score += 40

    return score


def find_best_section(query):

    best = None
    best_score = 0

    for section in SECTIONS:

        s = score_section(query, section)

        if s > best_score:
            best_score = s
            best = section

    return best


# -----------------------------
# HELPERS
# -----------------------------

def summarize_text(text, sentences=2):

    parts = re.split(r'(?<=[.!?])\s+', text)

    return " ".join(parts[:sentences])


def explain_text(text, max_chars=600):

    text = text.strip()

    if len(text) < max_chars:
        return text

    short = text[:max_chars]

    last_period = short.rfind(".")

    if last_period > 100:
        return short[:last_period + 1]

    return short + "..."


# -----------------------------
# CHATBOT
# -----------------------------

def ninjettriss_reply(user_text):

    global LAST_TOPIC

    q = normalize_typos(user_text)

    if any(x in q for x in ["hello", "hi", "hey"]):

        return "Ninjettriss says: Welcome, puny mortal. Ask me about the doctrine and I shall guide you."


    if "alien weed cult" in q or "what is the cult" in q:

        return (
            "Ninjettriss says: The Alien Weed Cult is an advanced sorcerer tech "
            "designed to prepare one for death by training one to recognize the "
            "ultimate nature of mind. It guides practitioners through a four-stage "
            "model that stabilizes awareness, dissolves ego grasping, and trains "
            "lucidity during dying."
        )


    if "four stage" in q or "four stages" in q:

        return (
            "Ninjettriss says: The Alien Weed Cult follows a four-stage model.\n\n"
            "First is Ninjitzu Resting, learning to rest in direct awareness.\n\n"
            "Second is Ninjitzu Illusion, examining the interdependent nature of reality and self.\n\n"
            "Third is Ninjitzu Yenfo-Tech, the body method regulating the nervous system.\n\n"
            "Fourth is Death Ninjitzu, training awareness to remain lucid during dying."
        )


    if "summarize" in q and LAST_TOPIC:

        return "Ninjettriss says: " + summarize_text(LAST_TOPIC)


    if "what does that mean" in q and LAST_TOPIC:

        return "Ninjettriss says: " + summarize_text(LAST_TOPIC, 3)


    section = find_best_section(q)

    if section:

        LAST_TOPIC = section["content"]

        return "Ninjettriss says: " + explain_text(section["content"])


    return random.choice([
        "Ninjettriss says: Ask about the doctrine.",
        "Ninjettriss says: Speak clearly, mortal.",
        "Ninjettriss says: Try asking about the four-stage model.",
        "Ninjettriss says: My wisdom is vast but your question is unclear."
    ])


# -----------------------------
# ROUTES
# -----------------------------

@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(".", path)


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json(silent=True) or {}

    user_message = data.get("message", "")

    user_message = normalize_typos(user_message)

    reply = ninjettriss_reply(user_message)

    return jsonify({"reply": reply})


# -----------------------------
# RUN
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True, port=8000)
