"""
model.py
Lightweight NLP inference helpers with an optional transformers fallback.

Exports analyze_message(text) -> {
    sentiment,
    sentiment_score,
    toxicity,
    subjectivity
}
"""

from typing import Dict

MODEL_AVAILABLE = False

SENTIMENT_MAP = {
    "label_0": "negative",
    "label_1": "neutral",
    "label_2": "positive",
}

try:
    from transformers import pipeline
    try:
        sentiment_model = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment"
        )
        toxicity_model = pipeline(
            "text-classification",
            model="unitary/toxic-bert"
        )
        MODEL_AVAILABLE = True
    except Exception:
        MODEL_AVAILABLE = False
except Exception:
    MODEL_AVAILABLE = False


# --------------------------------------------------
# Heuristic fallback
# --------------------------------------------------

def _heuristic_analyze(text: str) -> Dict:
    neg_words = {
        "hate", "stupid", "idiot", "useless", "worst",
        "fault", "blame", "never", "always", "stop",
        "dont", "can't", "cant", "tolerate", "like"
    }

    tox_words = {"kill", "die", "attack", "terror"}

    text_lower = (text or "").lower()

    neg_count = sum(1 for w in neg_words if w in text_lower)
    tox_count = sum(1 for w in tox_words if w in text_lower)

    sentiment = "negative" if neg_count > 0 else "neutral"
    sentiment_score = min(0.9, 0.4 + neg_count * 0.25)

    return {
        "sentiment": sentiment,
        "sentiment_score": round(sentiment_score, 3),
        "toxicity": round(min(1.0, tox_count * 0.3), 3),
        "subjectivity": round(min(1.0, sentiment_score + 0.2), 3),
    }


# --------------------------------------------------
# Public API
# --------------------------------------------------

def analyze_message(text: str) -> Dict:
    if not text or not text.strip():
        return {
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "toxicity": 0.0,
            "subjectivity": 0.0,
        }

    if MODEL_AVAILABLE:
        try:
            sent = sentiment_model(text)[0]
            tox = toxicity_model(text)[0]

            raw_label = sent.get("label", "neutral").lower()
            sentiment = SENTIMENT_MAP.get(raw_label, raw_label)
            sentiment_score = float(sent.get("score", 0.0))

            toxicity = (
                float(tox.get("score", 0.0))
                if tox.get("label", "").lower() == "toxic"
                else 0.0
            )

            subjectivity = min(1.0, sentiment_score + toxicity)

            return {
                "sentiment": sentiment,
                "sentiment_score": round(sentiment_score, 3),
                "toxicity": round(toxicity, 3),
                "subjectivity": round(subjectivity, 3),
            }
        except Exception:
            return _heuristic_analyze(text)
    else:
        return _heuristic_analyze(text)


if __name__ == "__main__":
    print(analyze_message("i dont like you"))
