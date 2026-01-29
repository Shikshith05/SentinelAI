"""
SentinalAI - Conflict Detection System
Streamlit Frontend with Real-time Conflict Analysis
"""

import streamlit as st
from datetime import datetime

from model import analyze_message as model_analyze
from rules import apply_rules

# Page configuration
st.set_page_config(
    page_title="SentinalAI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark mode styling
st.markdown("""
<style>
    .main { padding: 0; }
    .stColumns { gap: 0; }
    h1 { color: #7c3aed; text-shadow: 0 0 20px rgba(124, 58, 237, 0.3); }
    h2 { color: #a78bfa; font-size: 1.3em; }
    .info-box {
        background-color: #1e3a5f;
        border-left: 4px solid #60a5fa;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
        color: #e0e7ff;
    }
</style>
""", unsafe_allow_html=True)

# Demo conversation data with more examples
DEMO_MESSAGES = {
    "Alice": [
        ("Alice", "This project is going nowhere!", "10:23", "high"),
        ("Bob", "I disagree. We're making progress.", "10:24", "medium"),
        ("Alice", "Your idea is completely useless.", "10:25", "high"),
        ("Manager", "Let's discuss this constructively.", "10:26", "medium"),
    ],
    "Bob": [
        ("Bob", "You never listen to my ideas!", "14:05", "high"),
        ("Manager", "Let's take a step back and discuss.", "14:06", "low"),
        ("Bob", "I appreciate your feedback on this.", "14:07", "low"),
        ("Alice", "Good point, let's work together.", "14:08", "low"),
    ],
    "Manager": [
        ("Manager", "Both of you need to communicate better.", "09:15", "medium"),
        ("Alice", "Understood. I'll make more effort.", "09:16", "low"),
        ("Bob", "Thanks for the guidance.", "09:17", "low"),
        ("Manager", "Great! Let's continue working as a team.", "09:18", "low"),
    ]
}

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = {}
    for user in DEMO_MESSAGES:
        st.session_state.messages[user] = list(DEMO_MESSAGES[user])

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None

def analyze_text(text: str) -> dict:
    """Analyze text using ML + rules"""

    try:
        model_output = model_analyze(text)
        model_error = None
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

    # Count caps (SHOUTING)
    caps_count = sum(1 for c in text if c.isupper())
    if text and caps_count > len(text) * 0.3:
        conflict_score = min(100, conflict_score + 10)
        flags.append("⚠️ Excessive caps detected (aggressive tone)")

    # Count exclamation marks
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


# Header
st.markdown("""
    <h1 style='text-align: center; margin-bottom: 5px;'> SentinalAI</h1>
    <p style='text-align: center; color: #a78bfa; margin-bottom: 20px; font-weight: bold;'>Real-time Conflict Detection & De-escalation Assistant</p>
    <p style='text-align: center; color: #cbd5e1; font-size: 0.9em; margin-bottom: 20px;'>Analyze conversations to identify tension escalation and receive AI-powered suggestions for constructive communication</p>
    """, unsafe_allow_html=True)

st.divider()

# Main 2-column layout
col_chat, col_analysis = st.columns(2, gap="small")

# LEFT COLUMN: Chat Section
with col_chat:
    st.subheader(" Chat Section")
    st.write("View and participate in conversations with different personas")

    # User selector with descriptions
    user_descriptions = {
        "Alice": "Assertive, sometimes aggressive communicator",
        "Bob": "Analytical, can be dismissive of others",
        "Manager": "Mediator focused on resolution"
    }

    user = st.selectbox(
        "Select User:",
        options=[""] + list(DEMO_MESSAGES.keys()),
        label_visibility="collapsed"
    )

    if user:
        st.session_state.current_user = user

        # Show user description
        st.caption(f" {user}: {user_descriptions.get(user, '')}")

        # Messages container with scrollable area
        st.markdown("**Conversation History:**")
        messages_placeholder = st.container()

        with messages_placeholder:
            for sender, text, timestamp, severity in st.session_state.messages[user]:
                if severity == "high":
                    st.markdown(f"<div style='background: #7f1d1d; border-left: 4px solid #ff6b6b; padding: 12px; border-radius: 6px; margin-bottom: 10px;'><strong style='color: #ff9999;'> {sender}</strong> <small style=\"color:#cbd5e1\">{timestamp}</small><br/><div style='margin-top: 6px; color: #fca5a5;'>{text}</div></div>", unsafe_allow_html=True)
                elif severity == "medium":
                    st.markdown(f"<div style='background: #78350f; border-left: 4px solid #fbbf24; padding: 12px; border-radius: 6px; margin-bottom: 10px;'><strong style='color: #fcd34d;'> {sender}</strong> <small style=\"color:#cbd5e1\">{timestamp}</small><br/><div style='margin-top: 6px; color: #fed7aa;'>{text}</div></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='background: #064e3b; border-left: 4px solid #34d399; padding: 12px; border-radius: 6px; margin-bottom: 10px;'><strong style='color: #6ee7b7;'> {sender}</strong> <small style=\"color:#cbd5e1\">{timestamp}</small><br/><div style='margin-top: 6px; color: #a7f3d0;'>{text}</div></div>", unsafe_allow_html=True)

        st.divider()

        # Message statistics
        col_stats1, col_stats2 = st.columns(2)
        with col_stats1:
            st.metric("Messages in Chat", len(st.session_state.messages[user]))
        with col_stats2:
            high_severity = sum(1 for _, _, _, sev in st.session_state.messages[user] if sev == "high")
            st.metric(" High Tension Messages", high_severity)

        st.divider()

        # Message input
        st.markdown("**Send a Message:**")
        col_input, col_send = st.columns([4, 1])
        with col_input:
            new_message = st.text_input(
                " Message for your friend",
                label_visibility="collapsed",
                key="message_input",
                placeholder="Type your message here..."
            )

        with col_send:
            send_button = st.button("Send", use_container_width=True, type="primary")

        if send_button and new_message:
            # Analyze the message
            analysis = analyze_text(new_message)
            st.session_state.last_analysis = analysis

            # Add message to conversation
            timestamp = datetime.now().strftime("%H:%M")
            st.session_state.messages[user].append(
                (user, new_message, timestamp, analysis["severity"]) 
            )

            # Clear input and rerun
            st.toast(f"Message sent! Analysis: {analysis['severity'].upper()} severity", icon="✅")
            st.rerun()
    else:
        st.info(" Select a user from the dropdown to start viewing and analyzing conversations")


# RIGHT COLUMN: Conflict Analysis Panel
with col_analysis:
    st.subheader(" Conflict Analysis Panel")
    st.write("Real-time analysis of conversation tone and conflict indicators")

    if st.session_state.current_user and st.session_state.last_analysis:
        analysis = st.session_state.last_analysis
    elif st.session_state.current_user:
        # Analyze the last message in the conversation
        last_user, last_text, _, _ = st.session_state.messages[st.session_state.current_user][-1]
        analysis = analyze_text(last_text)
        st.session_state.last_analysis = analysis
    else:
        analysis = None

    if analysis:
        st.divider()

        # Risk Meter (Large and prominent)
        st.markdown("###  Conflict Score")
        score = analysis["conflict_score"]

        # Create progress bar with interpretation
        st.progress(score / 100, text=f"{score}% - {analysis['severity'].upper()}")

        # Risk interpretation
        if score < 40:
            risk_text = " LOW RISK: Conversation is constructive and positive"
            risk_color = "#064e3b"
            risk_text_color = "#a7f3d0"
        elif score < 70:
            risk_text = " MEDIUM RISK: Some tension present, needs monitoring"
            risk_color = "#78350f"
            risk_text_color = "#fed7aa"
        else:
            risk_text = " HIGH RISK: Significant conflict escalation detected"
            risk_color = "#7f1d1d"
            risk_text_color = "#fca5a5"

        st.markdown(f"<div style='background: {risk_color}; padding: 12px; border-radius: 6px; text-align: center; font-weight: bold; color: {risk_text_color};'>{risk_text}</div>", unsafe_allow_html=True)

        st.divider()

        # Detected Flags (with explanation)
        st.markdown("###  Detected Conflict Indicators")
        if analysis["flags"]:
            for flag in analysis["flags"]:
                st.markdown(f" {flag}")
        else:
            st.markdown("✅ No negative indicators detected")
        
        # Show triggered rules
        if analysis["triggered_rules"]:
            st.caption(
                "**Rules triggered:** "
                + ", ".join([f"`{rule.replace('_', ' ')}`" for rule in analysis["triggered_rules"]])
            )
        
        st.divider()

        # AI Suggestion (prominent)
        st.markdown("###  AI-Powered Suggestion")
        st.info(analysis["suggestion"], icon="🤖")

        st.divider()

        # Message Analysis Details
        st.markdown("### 📋 Message Details")
        col_detail1, col_detail2, col_detail3 = st.columns(3)
        with col_detail1:
            st.metric("Word Count", analysis["word_count"])
        with col_detail2:
            st.metric("Sentiment", analysis["model"]["sentiment"].upper())
            st.caption(f"Score: {analysis['model']['sentiment_score']}")
        with col_detail3:
            st.metric("Toxicity", f"{analysis['model']['toxicity']}")

        if analysis.get("model_error"):
            st.warning("Model fallback used. Check model.py dependencies or model download.")
        
        st.divider()

        # Tips section
        with st.expander(" Communication Tips", expanded=False):
            st.markdown("""
            **For Low Tension ():**
            - Continue open dialogue
            - Acknowledge good points
            - Maintain respectful tone
            
            **For Medium Tension ():**
            - Use "I" statements instead of "you" accusations
            - Ask clarifying questions
            - Acknowledge different perspectives
            - Take breaks if needed
            
            **For High Tension ():**
            - Pause the conversation
            - Find common ground
            - Use active listening
            - Consider involving a mediator
            - Focus on solutions, not blame
            """)

        st.divider()

        # Conversation health
        if st.session_state.current_user:
            st.markdown("###  Conversation Health")
            user_msgs = st.session_state.messages[st.session_state.current_user]
            high_count = sum(1 for _, _, _, sev in user_msgs if sev == "high")
            med_count = sum(1 for _, _, _, sev in user_msgs if sev == "medium")
            low_count = sum(1 for _, _, _, sev in user_msgs if sev == "low")

            col_h1, col_h2, col_h3 = st.columns(3)
            with col_h1:
                st.metric(" Positive", low_count)
            with col_h2:
                st.metric(" Neutral", med_count)
            with col_h3:
                st.metric(" Tense", high_count)
    else:
        st.info(" Select a user to start analyzing conflicts")
