"""
rules.py
Explainable conflict + tone detection using compositional linguistic signals.

This version correctly flags:
• negative tone without "you"
• rejection / dissatisfaction
• norm violations (profanity)
• interpersonal conflict
"""

from typing import Dict
import re


# --------------------------------------------------
# Signal vocabularies
# --------------------------------------------------

SECOND_PERSON = {"you", "your", "you're", "youve"}

ABSOLUTES = {"always", "never", "nothing", "every"}

DIRECTIVES = {"stop", "fix", "explain", "do", "dont", "don't"}

DISCOURSE_MARKERS = {"but", "clearly", "obviously"}

NEGATIONS = {"not", "dont", "don't", "cant", "can't", "cannot"}

REJECTION_VERBS = {"like", "tolerate", "stand", "respect", "accept"}

NEGATIVE_EVALUATIONS = {
    "unacceptable", "nonsense", "ridiculous",
    "inappropriate", "wrong", "bad", "terrible", "useless"
}

PROFANITY = {
    "fuck", "shit", "damn", "asshole", "bitch"
}


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def tokenize(text: str):
    return re.findall(r"\b\w+\b", text.lower())


def count_overlap(tokens, vocab):
    return sum(1 for t in tokens if t in vocab)


def has_second_person(tokens):
    return count_overlap(tokens, SECOND_PERSON) > 0


# --------------------------------------------------
# Pattern detectors
# --------------------------------------------------

def rejection_pattern(tokens):
    return (
        count_overlap(tokens, REJECTION_VERBS) > 0
        and count_overlap(tokens, NEGATIONS) > 0
    )


def blame_pattern(tokens, sentiment_score):
    return (
        has_second_person(tokens)
        and (
            count_overlap(tokens, ABSOLUTES) > 0
            or sentiment_score > 0.6
        )
    )


def confrontational_pattern(tokens, sentiment_score):
    return (
        count_overlap(tokens, DIRECTIVES) > 0
        and sentiment_score > 0.55
    )


def negative_tone_pattern(tokens):
    return (
        count_overlap(tokens, NEGATIVE_EVALUATIONS) > 0
        or ("dont" in tokens and "like" in tokens)
    )


def norm_violation(tokens):
    return count_overlap(tokens, PROFANITY) > 0


# --------------------------------------------------
# Feature extraction
# --------------------------------------------------

def extract_rule_features(text: str, model_output: Dict) -> Dict:
    tokens = tokenize(text)

    sentiment = model_output["sentiment"]
    sentiment_score = model_output["sentiment_score"]
    toxicity = model_output["toxicity"]

    return {
        # Tone-level conflict (no target required)
        "negative_tone": negative_tone_pattern(tokens),
        "norm_violation": norm_violation(tokens),

        # Interpersonal conflict
        "negative_interaction": sentiment == "negative" and has_second_person(tokens),
        "rejection": rejection_pattern(tokens),
        "blame": blame_pattern(tokens, sentiment_score),
        "confrontational": confrontational_pattern(tokens, sentiment_score),

        # Severe
        "toxic": toxicity > 0.4,
    }


# --------------------------------------------------
# Conflict scoring
# --------------------------------------------------

def calculate_conflict_score(features: Dict) -> float:
    score = 0.0

    weights = {
        "negative_tone": 0.3,
        "norm_violation": 0.6,

        "negative_interaction": 0.2,
        "rejection": 0.35,
        "blame": 0.3,
        "confrontational": 0.25,

        "toxic": 0.5,
    }

    for k, w in weights.items():
        if features.get(k):
            score += w

    # Synergy bonuses
    if features["negative_tone"] and features["rejection"]:
        score += 0.15

    if features["blame"] and features["confrontational"]:
        score += 0.15

    return min(score, 1.0)


# --------------------------------------------------
# Public API
# --------------------------------------------------

def apply_rules(text: str, model_output: Dict) -> Dict:
    features = extract_rule_features(text, model_output)
    score = calculate_conflict_score(features)

    if score < 0.3:
        risk = "LOW"
        recommendation = "No action needed"
    elif score < 0.6:
        risk = "MEDIUM"
        recommendation = "Suggest cooling-off or rephrasing"
    else:
        risk = "HIGH"
        recommendation = "Intervene or alert moderator"

    return {
        "conflict_score": round(score, 3),
        "risk_level": risk,
        "recommendation": recommendation,
        "triggered_rules": [k for k, v in features.items() if v],
    }


# --------------------------------------------------
# Manual test
# --------------------------------------------------

if __name__ == "__main__":
    sample = {
        "sentiment": "negative",
        "sentiment_score": 0.75,
        "toxicity": 0.1,
    }

    tests = [
        "i dont like this behaviour",
        "i dont like this tone",
        "this is not acceptable",
        "what nonsense is this",
        "fuck you",
    ]

    for t in tests:
        print(t, "->", apply_rules(t, sample))
