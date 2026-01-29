"""
rules.py
Rule-based conflict detection layer.

Consumes outputs from model.py (RoBERTa + Toxicity)
and applies explainable conflict escalation logic.
"""

from typing import Dict, List


# --------------------------------------------------
# Phrase groups (organized & weighted)
# --------------------------------------------------

BLAME_PHRASES = [
    "you always", "you never", "your fault", "because of you",
    "you caused", "you messed", "you should have"
]

PASSIVE_AGGRESSIVE_PHRASES = [
    "fine then", "whatever you think", "if you insist",
    "sure, okay", "do what you want", "as usual"
]

ESCALATION_PHRASES = [
    "this is unacceptable", "i'm done", "we need to talk",
    "this ends now"
]

SARCASM_PHRASES = [
    "yeah right", "sure...", "nice job", "great idea",
    "thanks a lot"
]


# --------------------------------------------------
# Helper functions
# --------------------------------------------------


def contains_any(text: str, phrases: List[str]) -> bool:
    text = text.lower()
    return any(p in text for p in phrases)


def contains_second_person(text: str) -> bool:
    text = text.lower()
    return any(p in text.split() for p in ["you", "your", "you're"])


# --------------------------------------------------
# Feature extraction (RULE CONDITIONS)
# --------------------------------------------------


def extract_rule_features(text: str, model_output: Dict) -> Dict:
    """
    Combine linguistic rules + model predictions into features
    """

    sentiment = model_output["sentiment"]
    sentiment_score = model_output["sentiment_score"]
    toxicity = model_output["toxicity"]

    features = {
        # Model-driven
        "negative_sentiment": sentiment == "negative",
        "high_negativity": sentiment == "negative" and sentiment_score > 0.6,
        "toxic": toxicity > 0.5,

        # Combination-based linguistic rules
        "blame_language": (
            contains_any(text, BLAME_PHRASES)
            and contains_second_person(text)
            and sentiment == "negative"
        ),

        "passive_aggressive": (
            contains_any(text, PASSIVE_AGGRESSIVE_PHRASES)
            and sentiment != "positive"
        ),

        "sarcasm": (
            contains_any(text, SARCASM_PHRASES)
            and sentiment != "positive"
        ),

        "escalation_language": (
            contains_any(text, ESCALATION_PHRASES)
            and sentiment == "negative"
        )
    }

    return features


# --------------------------------------------------
# Conflict score computation
# --------------------------------------------------


def calculate_conflict_score(features: Dict) -> float:
    """
    Convert rule features into a single conflict score
    """

    score = 0.0

    if features["high_negativity"]:
        score += 0.25

    if features["blame_language"]:
        score += 0.30

    if features["passive_aggressive"]:
        score += 0.20

    if features["sarcasm"]:
        score += 0.15

    if features["escalation_language"]:
        score += 0.35

    if features["toxic"]:
        score += 0.50

    return min(score, 1.0)


# --------------------------------------------------
# Final rule engine (used by Streamlit)
# --------------------------------------------------


def apply_rules(text: str, model_output: Dict) -> Dict:
    """
    Main rule engine entry point
    """

    features = extract_rule_features(text, model_output)
    conflict_score = calculate_conflict_score(features)

    # Risk levels
    if conflict_score < 0.3:
        risk = "LOW"
        recommendation = "No action needed"
    elif conflict_score < 0.6:
        risk = "MEDIUM"
        recommendation = "Suggest cooling-off or private discussion"
    else:
        risk = "HIGH"
        recommendation = "Intervene or alert moderator"

    return {
        "conflict_score": round(conflict_score, 3),
        "risk_level": risk,
        "recommendation": recommendation,
        "triggered_rules": [k for k, v in features.items() if v]
    }


# --------------------------------------------------
# Optional test
# --------------------------------------------------


if __name__ == "__main__":
    sample_model_output = {
        "sentiment": "negative",
        "sentiment_score": 0.82,
        "toxicity": 0.67
    }

    text = "You always do this. This is your fault."
    print(apply_rules(text, sample_model_output))
