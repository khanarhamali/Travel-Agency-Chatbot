import os
import re
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import login

from langchain_huggingface import HuggingFacePipeline
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda

from ChatModels.documentloader import load_documents
from ChatModels.textsplitter import split_documents
from ChatModels.vectorstore import create_vectorstore
from ChatModels.retriever import create_retriever
from ChatModels.prompt import get_prompt

# ==========================
# Base Directory
# ==========================
BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================
# Predefined Questions (ONLY)
# ==========================
ALLOWED_QUESTIONS = [
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

# ==========================
# Load ENV
# ==========================
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

HF_TOKEN = os.getenv("HUGGINGFACEHUB_ACCESS_TOKEN")
if HF_TOKEN:
    login(token=HF_TOKEN)

# ==========================
# Utility Functions
# ==========================
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def clean_text(text: str) -> str:
    """
    Clean and format model output into bullet points.
    """
    text = re.sub(r"(Answer:|Context:|Question:)", "", text, flags=re.IGNORECASE)

    lines = re.split(r"\n|•|-|\d+\.", text)

    bullets = []
    seen = set()

    for line in lines:
        line = line.strip()

        if not line or line.endswith("?"):
            continue

        if len(line) < 4:
            continue

        if line.lower() not in seen:
            seen.add(line.lower())
            bullets.append(f"• {line}")

    if not bullets:
        return "• Information not found in the document."

    return "\n".join(bullets)

# ==========================
# Chat Model Class
# ==========================
class TravelChatModel:
    def __init__(self, pdf_name="travel_agency_chatbot_document.pdf"):

        print("🚀 Initializing Travel Chatbot...")

        # ✅ Lightweight & stable model
        self.llm = HuggingFacePipeline.from_model_id(
            model_id="google/flan-t5-small",
            task="text2text-generation",
            pipeline_kwargs={
                "max_new_tokens": 200,
            },
        )

        # ==========================
        # PDF Path
        # ==========================
        pdf_path = BASE_DIR / pdf_name
        if not pdf_path.exists():
            raise FileNotFoundError(f"❌ PDF file not found: {pdf_path}")

        print(f"📄 PDF loaded: {pdf_path}")

        # Load documents
        documents = load_documents(str(pdf_path))
        chunks = split_documents(documents)

        # Vectorstore + Retriever
        vectorstore = create_vectorstore(chunks)
        retriever = create_retriever(vectorstore)

        # Prompt
        prompt = get_prompt()

        # RAG Chain
        self.chain = (
            RunnableParallel(
                {
                    "context": retriever | RunnableLambda(format_docs),
                    "question": RunnablePassthrough(),
                }
            )
            | prompt
            | self.llm
        )

        print("✅ Chatbot Ready (Predefined Questions Mode)")

    # ==========================
    # Ask Function (Restricted)
    # ==========================
    def ask(self, question: str) -> str:

        # 🔒 Allow only predefined questions
        if question not in ALLOWED_QUESTIONS:
            return "• Please select a question from the available options."

        response = self.chain.invoke(question)
        return clean_text(response)
