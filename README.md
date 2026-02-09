# Travel Agency Chatbot

This repository contains a Streamlit-based Travel Assistant Chatbot. The chatbot leverages a Hugging Face LLM combined with a RAG (Retrieval-Augmented Generation) setup to answer travel-related queries using a PDF knowledge base.  

---

## Features

- Interactive chatbot interface using Streamlit.
- Predefined dropdown questions and custom queries.
- Uses vector search on PDF documents to provide accurate answers.
- Responses are formatted as clean bullet points.
- Session management to maintain conversation history.

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/khanarhamali/Travel-Agency-Chatbot.git
cd Travel-Agency-Chatbot
```
## Create a virtual environment and activate it:

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

## Install required packages:

pip install -r requirements.txt

## Create a .env file at the project root with your Hugging Face token:

HUGGINGFACEHUB_ACCESS_TOKEN=your_token_here

## Start the Streamlit app:

streamlit run app.py

## Project Structure

.
├── app.py                # Streamlit main app
├── chatmodel.py          # Chatbot class with LLM and RAG integration
├── documentloader.py     # PDF document loader
├── outputparser.py       # Model output cleaning and formatting
├── prompt.py             # Prompt template for the chatbot
├── retriever.py          # Vector search retriever
├── schema.py             # Pydantic schema for structured answers
├── textsplitter.py       # Document splitting logic
├── vectorstore.py        # Vector store creation using FAISS
├── requirements.txt      # Python dependencies
├── .gitignore            # Files to exclude from Git
└── .streamlit/config.toml # Streamlit configuration
