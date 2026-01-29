"""
SentinalAI - Streamlit Frontend UI
Main application entry point for the conflict detection interface
"""

import streamlit as st

def main():
    st.set_page_config(page_title="SentinalAI", layout="wide")
    st.title("🛡️ SentinalAI")
    st.subheader("Conflict Detection and Intervention")

if __name__ == "__main__":
    main()
