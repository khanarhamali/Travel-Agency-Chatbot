import os
import re
from pathlib import Path
from typing import List

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
# Predefined Questions (for quick selection)
# ==========================
ALLOWED_QUESTIONS: List[str] = [
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
# Load Environment Variables
# ==========================
def load_env():
    env_path = BASE_DIR / ".env"
    load_dotenv(dotenv_path=env_path)
    token = os.getenv("HUGGINGFACEHUB_ACCESS_TOKEN")
    if token:
        login(token=token)
    return token

HF_TOKEN = load_env()

# ==========================
# Utility Functions
# ==========================
def format_docs(docs) -> str:
    return "\n\n".join(doc.page_content for doc in docs)

def clean_output(text: str) -> str:
    """
    Clean and format LLM output into bullet points.
    """
    text = re.sub(r"(Answer:|Context:|Question:)", "", text, flags=re.IGNORECASE)

    lines = re.split(r"\n|•|-|\d+\.", text)

    bullets = []
    seen = set()

    for line in lines:
        line = line.strip()
        if not line or len(line) < 4:
            continue
        key = line.lower()
        if key not in seen:
            seen.add(key)
            bullets.append(f"• {line}")

    return "\n".join(bullets) if bullets else "• Information not found in the document."

# ==========================
# Travel Chatbot Model
# ==========================
class TravelChatModel:
    """
    RAG-based Travel Chatbot with both predefined and dynamic question support.
    """

    def __init__(self, pdf_name: str = "travel_agency_chatbot_document.pdf"):
        print("🚀 Initializing Travel Chatbot...")

        # -------- LLM Setup --------
        self.llm = HuggingFacePipeline.from_model_id(
            model_id="google/flan-t5-small",
            task="text2text-generation",
            pipeline_kwargs={
                "max_new_tokens": 200,
                "temperature": 0.3,
            },
        )

        # -------- PDF Loading --------
        pdf_path = BASE_DIR / pdf_name
        if not pdf_path.exists():
            raise FileNotFoundError(f"❌ PDF file not found: {pdf_path}")

        print(f"📄 Loaded PDF: {pdf_path.name}")

        documents = load_documents(str(pdf_path))
        chunks = split_documents(documents)

        # -------- Vectorstore & Retriever --------
        vectorstore = create_vectorstore(chunks)
        retriever = create_retriever(vectorstore)

        # -------- Prompt --------
        prompt = get_prompt()

        # -------- RAG Chain --------
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

        print("✅ Travel Chatbot Ready (Dynamic Mode Enabled)")

    # ==========================
    # Main Ask Function
    # ==========================
    def ask(self, question: str) -> str:
        """
        Answer both predefined and dynamic questions using RAG.
        """
        if not question.strip():
            return "• Please ask a valid question."

        try:
            response = self.chain.invoke(question)
            return clean_output(response)
        except Exception as e:
            return f"• Sorry, something went wrong: {str(e)}"

    # ==========================
    # Helper Method
    # ==========================
    def get_allowed_questions(self) -> List[str]:
        """
        Return predefined quick questions.
        """
        return ALLOWED_QUESTIONS
