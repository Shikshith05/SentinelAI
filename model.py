"""
model.py
Lightweight NLP inference helpers with an optional transformers fallback.

The module exports `analyze_message(text)` which returns a dict with
`sentiment`, `sentiment_score`, and `toxicity`. If `transformers` is
available and models can be loaded, it will use them; otherwise a small
heuristic fallback is used so the Streamlit app can run offline.
"""

from typing import Dict

MODEL_AVAILABLE = False
try:
    from transformers import pipeline
    # Lazy model loading: wrap in try to avoid failing import on environments
    try:
        sentiment_model = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
        toxicity_model = pipeline("text-classification", model="unitary/toxic-bert")
        MODEL_AVAILABLE = True
    except Exception:
        MODEL_AVAILABLE = False
except Exception:
    MODEL_AVAILABLE = False


def _heuristic_analyze(text: str) -> Dict:
    neg_words = ["hate", "stupid", "idiot", "useless", "worst", "fault", "blame", "never"]
    tox_words = ["kill", "die", "attack", "terror"]

    text_lower = (text or "").lower()
    neg_count = sum(1 for w in neg_words if w in text_lower)
    tox_count = sum(1 for w in tox_words if w in text_lower)

    if neg_count == 0:
        sentiment = "neutral"
        sentiment_score = 0.5
    elif neg_count == 1:
        sentiment = "negative"
        sentiment_score = 0.65
    else:
        sentiment = "negative"
        sentiment_score = 0.9

    toxicity = min(1.0, 0.1 * tox_count)

    return {
        "sentiment": sentiment,
        "sentiment_score": round(sentiment_score, 3),
        "toxicity": round(toxicity, 3),
    }


def analyze_message(text: str) -> Dict:
    """Analyze input text and return sentiment/toxicity scores.

    Returns a dict with keys: `sentiment`, `sentiment_score`, `toxicity`.
    """

    if not text or not text.strip():
        return {"sentiment": "neutral", "sentiment_score": 0.0, "toxicity": 0.0}

    if MODEL_AVAILABLE:
        try:
            sent_result = sentiment_model(text)[0]
            sentiment_label = sent_result.get("label", "neutral").lower()
            sentiment_score = float(sent_result.get("score", 0.0))

            tox_result = toxicity_model(text)[0]
            tox_label = tox_result.get("label", "toxic").lower()
            tox_score = float(tox_result.get("score", 0.0)) if tox_label == "toxic" else 0.0

            return {
                "sentiment": sentiment_label,
                "sentiment_score": round(sentiment_score, 3),
                "toxicity": round(tox_score, 3),
            }
        except Exception:
            # If model inference fails, fall back to heuristic
            return _heuristic_analyze(text)
    else:
        return _heuristic_analyze(text)


if __name__ == "__main__":
    print(analyze_message("Stop blaming me. This is your fault."))
