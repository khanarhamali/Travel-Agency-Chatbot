from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st

from ChatModels.chatmodel import TravelChatModel

# ----------------------- Logging -----------------------
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "interactions.csv"

def log_interaction(user_text: str, reply: str) -> None:
    now = datetime.now().isoformat(timespec="seconds")
    df = pd.DataFrame([{
        "timestamp": now,
        "user_text": user_text,
        "bot_reply": reply
    }])
    file_exists = LOG_FILE.exists()
    df.to_csv(LOG_FILE, mode="a", index=False, header=not file_exists)

# ----------------------- Streamlit settings -----------------------
st.set_page_config(page_title="Travel Agency Chatbot", page_icon="🌍", layout="wide")

st.markdown("""
<style>
.block-container { max-width: 1000px !important; padding-top: 2rem !important; }
.chat-card { background: #1e1e1e; padding: 1.5rem; border-radius: 1rem; box-shadow: 0 8px 25px rgba(0,0,0,0.3); }
.stChatMessage p { font-size: 0.95rem; line-height: 1.5; color: #f1f1f1; }
div[data-baseweb="textarea"] textarea { border-radius: 12px !important; padding: 0.8rem 1rem !important; font-size: 0.95rem; background-color: #2c2c2c !important; color: #f1f1f1 !important; border: 1px solid #444 !important; }
div[data-baseweb="textarea"] textarea:focus { border: 1px solid #6c63ff !important; outline: none; }
.css-1n76uvr { background-color: #2c2c2c !important; color: #f1f1f1 !important; border-radius: 12px !important; }
section[data-testid="stSidebar"] { font-size: 0.9rem !important; }
.stMarkdown p { color: #f1f1f1; }
hr { margin: 1.5rem 0; border-color: #444; }
</style>
""", unsafe_allow_html=True)

# ---------------- Sidebar ----------------
st.sidebar.title("🌍 Travel Chatbot")
mode = st.sidebar.radio("Mode", ["Chat", "Analytics"])

# ---------- Sidebar Book a Tour Form ----------
st.sidebar.markdown("---")
st.sidebar.markdown("### 📩 Book a Tour Form")
st.sidebar.markdown(
    "If you want to book a tour after asking the chatbot, please fill out your contact details below. We will contact you soon."
)

with st.sidebar.form(key="book_tour_form"):
    name = st.text_input("Your Name *")
    email = st.text_input("Your Email *")
    phone = st.text_input("Your Phone Number *")
    submitted = st.form_submit_button("Submit")

    if submitted:
        if not name or not email or not phone:
            st.error("Please fill Name, Email, and Phone Number.")
        else:
            # Save to CSV
            CONTACTS_DIR = Path("contacts")
            CONTACTS_DIR.mkdir(exist_ok=True)
            CONTACTS_FILE = CONTACTS_DIR / "bookings.csv"

            now = datetime.now().isoformat(timespec="seconds")
            df = pd.DataFrame([{
                "timestamp": now,
                "name": name,
                "email": email,
                "phone": phone
            }])
            file_exists = CONTACTS_FILE.exists()
            df.to_csv(CONTACTS_FILE, mode="a", index=False, header=not file_exists)

            st.success("✅ Thank you! Your contact details have been submitted. We will reach out to you soon.")

# ------------- Session state -------------
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I’m your travel assistant 🌍\nSelect a question below."}]

if "chatbot" not in st.session_state:
    st.session_state.chatbot = TravelChatModel()

chatbot = st.session_state.chatbot

# ------------------- CHAT MODE -------------------
if mode == "Chat":
    st.title("Travel Agency Chatbot 🌍")
    st.button("✏️ Clear Chat", on_click=lambda: st.session_state.pop("messages", None))

    st.markdown('<div class="chat-card">', unsafe_allow_html=True)
    
    # Quick question dropdown
    st.markdown("**Quick Questions:**")
    selected_question = st.selectbox("Choose a question", options=chatbot.get_allowed_questions(), index=0)

    # Button to ask the selected question
    use_selected_question = st.button("Ask Selected Question")

    # Show chat history
    for msg in st.session_state.messages:
        avatar = "🤖" if msg["role"] == "assistant" else "🧑"
        with st.chat_message(msg["role"], avatar=avatar):
            timestamp = msg.get("time", "")
            st.markdown(f"<div style='text-align: right; font-size: 11px; color: #9CA3AF;'>{timestamp}</div>", unsafe_allow_html=True)
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Type your question here...")
    message_to_process = None

    # Process message only if user typed or clicked button
    if user_input:
        message_to_process = user_input
    elif use_selected_question:
        message_to_process = selected_question

    if message_to_process:
        timestamp = datetime.now().strftime("%I:%M %p")
        
        # Append user message
        st.session_state.messages.append({"role": "user", "content": message_to_process, "time": timestamp})

        with st.chat_message("user", avatar="🧑"):
            st.markdown(message_to_process)

        # Get bot reply
        reply = chatbot.ask(message_to_process)
        st.session_state.messages.append({"role": "assistant", "content": reply, "time": timestamp})

        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(reply)

        # Log interaction
        log_interaction(message_to_process, reply)

    st.markdown("</div>", unsafe_allow_html=True)

# ------------------- ANALYTICS MODE -------------------
else:
    st.title("📊 Analytics Dashboard")
    st.caption("Overview of user interactions with the chatbot.")

    if not LOG_FILE.exists():
        st.info("No interactions yet. Use Chat mode first.")
    else:
        df = pd.read_csv(LOG_FILE)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Messages", len(df))
        col2.metric("Unique Users", df["user_text"].nunique())
        col3.metric("Last Activity", df["timestamp"].max())

        st.markdown("---")
        st.subheader("Messages Overview")
        msg_counts = df["user_text"].value_counts().sort_values(ascending=False)
        st.bar_chart(msg_counts)

        st.subheader("Recent Interactions")
        df_sorted = df.sort_values("timestamp", ascending=False)
        st.dataframe(df_sorted.head(20), use_container_width=True)

        with st.expander("View Full Interaction Log"):
            st.dataframe(df, use_container_width=True)
