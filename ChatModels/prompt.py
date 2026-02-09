from langchain_core.prompts import PromptTemplate

PROMPT_TEMPLATE = """
You are a professional travel assistant.

Rules:
- Answer ONLY using the given context.
- Do NOT repeat the question.
- Do NOT ask questions.
- Write clear bullet points.
- If answer is not in context, say: "Information not found in the document."

Context:
{context}

Question:
{question}

Answer:
"""

def get_prompt():
    return PromptTemplate(
        input_variables=["context", "question"],
        template=PROMPT_TEMPLATE
    )
