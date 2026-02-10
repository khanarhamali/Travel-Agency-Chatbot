from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

BASE_DIR = Path(__file__).resolve().parent.parent
FAISS_PATH = BASE_DIR / "faiss_index"

def create_vectorstore(chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    if FAISS_PATH.exists():
        return FAISS.load_local(str(FAISS_PATH), embeddings, allow_dangerous_deserialization=True)

    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(str(FAISS_PATH))
    return vectorstore
