"""
SentinalAI - Conflict Detection System
FastAPI backend for the Next.js frontend.
"""

from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from model import analyze_message as model_analyze
from rules import apply_rules


class AnalyzeRequest(BaseModel):
    text: str


class SendMessageRequest(BaseModel):
    user: str
    text: str


class Message(BaseModel):
    sender: str
    text: str
    timestamp: str
    severity: str


app = FastAPI(title="SentinalAI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Single unified chat for all users
DEMO_MESSAGES: List[Message] = [
    Message(sender="Manager", text="Both of you need to communicate better.", timestamp="09:15", severity="medium"),
    Message(sender="Alice", text="Understood. I'll make more effort.", timestamp="09:16", severity="low"),
    Message(sender="Bob", text="Thanks for the guidance.", timestamp="09:17", severity="low"),
    Message(sender="Manager", text="Great! Let's continue working as a team.", timestamp="09:18", severity="low"),
    Message(sender="Alice", text="This project is going nowhere!", timestamp="10:23", severity="high"),
    Message(sender="Bob", text="I disagree. We're making progress.", timestamp="10:24", severity="medium"),
    Message(sender="Alice", text="Your idea is completely useless.", timestamp="10:25", severity="high"),
    Message(sender="Manager", text="Let's discuss this constructively.", timestamp="10:26", severity="medium"),
    Message(sender="Bob", text="You never listen to my ideas!", timestamp="14:05", severity="high"),
    Message(sender="Manager", text="Let's take a step back and discuss.", timestamp="14:06", severity="low"),
    Message(sender="Bob", text="I appreciate your feedback on this.", timestamp="14:07", severity="low"),
    Message(sender="Alice", text="Good point, let's work together.", timestamp="14:08", severity="low"),
]

MESSAGES: List[Message] = list(DEMO_MESSAGES)

INTERVENTION_THRESHOLD = 40
INTERVENTION_SENDER = "SentinalAI"
INTERVENTION_TEXT = (
    "Let's keep the conversation respectful and constructive. "
    "Please rephrase to avoid escalating conflict."
)


def analyze_text(text: str) -> Dict:
    """Analyze text using ML + rules."""

    try:
        model_output = model_analyze(text)
        model_error: Optional[str] = None
    except Exception as exc:
        model_output = {
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "toxicity": 0.0
        }
        model_error = str(exc)

    rules_output = apply_rules(text, model_output)

    risk_level = rules_output["risk_level"]
    severity_map = {
        "LOW": "low",
        "MEDIUM": "medium",
        "HIGH": "high"
    }
    severity = severity_map.get(risk_level, "low")

    conflict_score = int(round(rules_output["conflict_score"] * 100))
    flags = [f"Rule triggered: {r.replace('_', ' ').title()}" for r in rules_output["triggered_rules"]]

    caps_count = sum(1 for c in text if c.isupper())
    if text and caps_count > len(text) * 0.3:
        conflict_score = min(100, conflict_score + 10)
        flags.append("⚠️ Excessive caps detected (aggressive tone)")

    exclamation_count = text.count("!")
    if exclamation_count >= 3:
        conflict_score = min(100, conflict_score + 5)
        flags.append("⚠️ Multiple exclamation marks (strong emotion)")

    suggestion = rules_output["recommendation"]

    return {
        "conflict_score": conflict_score,
        "severity": severity,
        "flags": flags if flags else ["✅ No negative indicators"],
        "suggestion": suggestion,
        "word_count": len(text.split()),
        "triggered_rules": rules_output["triggered_rules"],
        "model": model_output,
        "model_error": model_error
    }


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/api/users")
def list_users() -> Dict[str, List[str]]:
    return {"users": ["Alice", "Bob", "Manager"]}


@app.get("/api/messages")
def get_messages() -> Dict[str, List[Message]]:
    return {"messages": MESSAGES}


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest) -> Dict:
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    return analyze_text(req.text)


@app.post("/api/send-message")
def send_message(req: SendMessageRequest) -> Dict:
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    analysis = analyze_text(req.text)
    timestamp = datetime.now().strftime("%H:%M")
    message = Message(sender=req.user, text=req.text, timestamp=timestamp, severity=analysis["severity"])
    MESSAGES.append(message)

    intervention_message: Optional[Message] = None
    if analysis["conflict_score"] >= INTERVENTION_THRESHOLD:
        intervention_message = Message(
            sender=INTERVENTION_SENDER,
            text=INTERVENTION_TEXT,
            timestamp=timestamp,
            severity="medium",
        )
        MESSAGES.append(intervention_message)

    return {
        "message": message,
        "analysis": analysis,
        "intervention": intervention_message
    }
