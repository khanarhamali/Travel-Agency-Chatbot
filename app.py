import streamlit as st
from ChatModels.chatmodel import TravelChatModel

# ==============================
# Load Chatbot
# ==============================
@st.cache_resource
def load_chatbot():
    return TravelChatModel()

chatbot = load_chatbot()

# ==============================
# Page Config
# ==============================
st.set_page_config(
    page_title="Travel Assistant Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Travel Assistant Chatbot")

st.write("Select a question from the list below 👇")

# ==============================
# Predefined Questions (ONLY 10)
# ==============================
QUESTIONS = [
    "How can I book a tour?",
    "What tour packages do you offer?",
    "What is included in a tour package?",
    "Do you provide guided tours?",
    "What are the best times to visit Pakistan?",
    "How much does a tour cost?",
    "Do you offer customized tours?",
    "What payment methods are available?",
    "How can I cancel or change a booking?",
    "How can I contact your travel agency?"
]

# ==============================
# Session State
# ==============================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==============================
# Dropdown Selection
# ==============================
selected_question = st.selectbox("Choose your question:", QUESTIONS)

if st.button("Ask"):
    st.session_state.messages.append({"role": "user", "content": selected_question})
    answer = chatbot.ask(selected_question)
    st.session_state.messages.append({"role": "assistant", "content": answer})

# ==============================
# Display Chat
# ==============================
st.divider()

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg["content"])
    else:
        st.chat_message("assistant").markdown(msg["content"])
