import streamlit as st
import requests
from datetime import datetime
import time
from streamlit_extras.stylable_container import stylable_container
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
USER_ID = os.getenv("USER_ID", "default_user")

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_id" not in st.session_state:
    st.session_state.user_id = USER_ID

# Authentication mock
def authenticate():
    if not st.session_state.authenticated:
        with st.sidebar:
            st.header("🔐 Authentication")
            user_id = st.text_input("Enter User ID", value=st.session_state.user_id)
            if st.button("Login"):
                st.session_state.user_id = user_id
                st.session_state.authenticated = True
                st.rerun()
        return False
    return True

# Custom CSS for modern look
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(135deg, #f8fafc 0%, #e0e7ef 100%);
    }
    .stTextArea textarea {
        background: #f4f7fb;
        border-radius: 8px;
        min-height: 100px;
        color: #333;
        caret-color: #333;
    }
    .response-box {
        background: #fff;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        padding: 1.2em 1em;
        margin-bottom: 1em;
        color: #333;
    }
    .history-expander > div {
        background: #f4f7fb !important;
        border-radius: 8px !important;
    }
    .footer {
        text-align: center;
        color: #888;
        font-size: 0.95em;
        margin-top: 2em;
    }
    .history-link {
        background: #f0f4f8;
        padding: 8px 16px;
        border-radius: 8px;
        margin: 10px 0;
        display: inline-block;
        color: #2563eb;
        text-decoration: none;
        font-weight: 500;
    }
    .history-link:hover {
        background: #e2e8f0;
    }
    .loading-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 2em 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Check authentication
if not authenticate():
    st.stop()

# UI Layout
st.markdown("""
    <h1 style='font-size:2.5em; font-weight:700; margin-bottom:0;'>🤖 AI Assistant</h1>
    <div style='color:#666; font-size:1.1em; margin-bottom:1.5em;'>Powered by Groq/Llama3 | <b>Today:</b> {}</div>
""".format(datetime.now().strftime("%Y-%m-%d")), unsafe_allow_html=True)

# Add history access link
history_url = f"{BACKEND_URL}/history?user_id={st.session_state.user_id}"
st.markdown(f"""
    <div style='margin-bottom: 1em;'>
        <a href='{history_url}' target='_blank' class='history-link'>
            📋 View Full History
        </a>
        <div style='font-size:0.9em; color:#666; margin-top:4px;'>
            Copy this link to access your history later: <code>{history_url}</code>
        </div>
    </div>
""", unsafe_allow_html=True)

# Sidebar for history and user info
with st.sidebar:
    st.header(f"👤 User: {st.session_state.user_id}")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
    
    st.header("🕑 Conversation History")
    if st.session_state.history:
        for idx, item in enumerate(st.session_state.history):
            with st.expander(f"{item['query'][:30]}...", expanded=False):
                st.caption(f"{item['time']}")
                st.markdown(f"<b>Query:</b> {item['query']}", unsafe_allow_html=True)
                st.divider()
                st.markdown(
                    f"<div class='response-box'><span style='font-size:1.2em;'>🎭</span> <b>Casual</b><br>{item['casual']}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div class='response-box'><span style='font-size:1.2em;'>📚</span> <b>Formal</b><br>{item['formal']}</div>",
                    unsafe_allow_html=True,
                )
    else:
        st.info("No history yet. Your conversations will appear here.")

# Main form
with stylable_container(css_styles="background: #fff; border-radius: 16px; padding: 2em 2em 1.5em 2em; box-shadow: 0 2px 12px rgba(0,0,0,0.06); margin-bottom:2em;"):
    with st.form("input_form"):
        query = st.text_area(
            "Enter your query:",
            placeholder="Explain quantum computing...",
            key="query_input",
        )
        submitted = st.form_submit_button("✨ Generate Response", use_container_width=True)

    if submitted:
        if not query.strip():
            st.error("Please enter a query")
        else:
            with st.spinner("Generating responses..."):
                start_time = time.time()
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/generate",
                        json={"user_id": st.session_state.user_id, "query": query}
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    # Show loading spinner
                    st.markdown("""
                        <div class='loading-spinner'>
                            <div class='spinner'></div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(
                            f"<div class='response-box'><span style='font-size:1.5em;'>🎭</span> <b>Casual Response</b><br>{data['casual_response']}</div>",
                            unsafe_allow_html=True,
                        )
                    with col2:
                        st.markdown(
                            f"<div class='response-box'><span style='font-size:1.5em;'>📚</span> <b>Formal Response</b><br>{data['formal_response']}</div>",
                            unsafe_allow_html=True,
                        )
                    st.session_state.history.insert(0, {
                        "query": query,
                        "casual": data['casual_response'],
                        "formal": data['formal_response'],
                        "time": datetime.now().strftime("%H:%M:%S")
                    })
                    st.success(f"Generated in {time.time()-start_time:.2f}s")
                except requests.exceptions.RequestException as e:
                    st.error(f"API Error: {str(e)}")

# Footer
st.markdown(
    """
    <div class='footer'>
        <hr style='margin:1em 0;'>
        <b>AI Assistant Prototype</b> &copy; 2025 &mdash; Built with ❤️ using Streamlit, FastAPI, and Groq/Llama3 by Kawaljeet Singh.
        <br>
        <span style='font-size:0.95em;'>For feedback, contact the developer.</span>
    </div>
    """,
    unsafe_allow_html=True,
)