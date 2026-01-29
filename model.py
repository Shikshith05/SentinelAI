"""
model.py
Handles all NLP inference using pretrained RoBERTa models.

Used directly by Streamlit app (no backend/API required).
"""

from transformers import pipeline

# --------------------------------------------------
# Load models ONCE (important)
# --------------------------------------------------

print("🔄 Loading AI models... (first run may take 1–2 minutes)")

# Sentiment model (positive / neutral / negative)
sentiment_model = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment"
)

# Toxicity model (toxic probability)
toxicity_model = pipeline(
    "text-classification",
    model="unitary/toxic-bert"
)

print("✅ Models loaded successfully!")


# --------------------------------------------------
# Main function used by Streamlit
# --------------------------------------------------

def analyze_message(text: str) -> dict:
    """
    Input:
        text (str) → chat message

    Output:
        {
            sentiment: positive/neutral/negative,
            sentiment_score: float,
            toxicity: float
        }
    """

    # Safety check
    if not text or not text.strip():
        return {
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "toxicity": 0.0
        }

    # ----------------------
    # Sentiment
    # ----------------------
    sent_result = sentiment_model(text)[0]

    sentiment_label = sent_result["label"].lower()
    sentiment_score = float(sent_result["score"])

    # ----------------------
    # Toxicity
    # ----------------------
    tox_result = toxicity_model(text)[0]

    if tox_result["label"].lower() == "toxic":
        toxicity_score = float(tox_result["score"])
    else:
        toxicity_score = 0.0

    # ----------------------
    # Return clean output
    # ----------------------
    return {
        "sentiment": sentiment_label,
        "sentiment_score": round(sentiment_score, 3),
        "toxicity": round(toxicity_score, 3)
    }


# --------------------------------------------------
# Optional quick test (run: python model.py)
# --------------------------------------------------

if __name__ == "__main__":
    test = "Stop blaming me. This is your fault."
    print(analyze_message(test))

