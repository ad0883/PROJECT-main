import streamlit as st
import time
import gemini  # Backend logic module
from datetime import datetime

# Basic page config
st.set_page_config(
    page_title="HealthNexus AI",
    page_icon="🩺",
)

# Minimal custom styling
st.markdown("""
    <style>
    .stApp header {
        background-color: transparent;
    }
    div.stChatMessage {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .user-info {
        font-size: 0.8rem;
        color: #666;
        padding: 0.5rem;
        margin-bottom: 1rem;
        background-color: #f8f9fa;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

def response_generator(prompt):
    response = gemini.generate_response(prompt)
    if not response:
        yield "No response generated."
        return
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

def exit_function():
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Goodbye! Have a great day! 👋"
    })
    gemini.save_chat_report_pdf()
    gemini.save_summary_report_pdf()
    time.sleep(2)
    st.rerun()

def js_refresh():
    st.markdown(
        """<script>window.location.reload();</script>""",
        unsafe_allow_html=True,
    )

# Display title and user info
st.title("🩺 HealthNexus AI")
st.subheader("Your AI-Powered Health Assistant")

# Display current time and user info
st.markdown(f"""
    <div class="user-info">
        🕒 UTC: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}<br>
        👤 User: ad0883
    </div>
""", unsafe_allow_html=True)

# Initialize chat messages with greeting
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": """👋 Hello! Welcome to HealthNexus AI!

I'm here to assist you with your health-related questions and concerns. How can I help you today?

You can ask me about:
• Health symptoms and conditions
• General medical advice
• Wellness tips
• Healthcare information

Feel free to start our conversation! 🌟"""
    }]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input handling
if prompt := st.chat_input("What's on your mind?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    if prompt.lower() in ["exit", "bye", "quit", "goodbye"]:
        with st.chat_message("assistant"):
            st.markdown("Goodbye! Have a great day! 👋")
        exit_function()
    else:
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            response = st.write_stream(response_generator(prompt))
        st.session_state.messages.append({"role": "assistant", "content": response})