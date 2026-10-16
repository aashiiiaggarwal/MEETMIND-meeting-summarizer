
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnablePassthrough,
    RunnableLambda,
)

from core.vector_store import (
    build_vector_store,
    load_vector_store,
    get_retriever,
)


def get_llm():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found. Check your .env file."
        )

    return ChatGoogleGenerativeAI(
        model="gemini-flash-lite-latest",
        google_api_key=api_key,
        temperature=0.2,
    )


def format_docs(docs) -> str:
    """Format retrieved transcript chunks clearly."""
    if not docs:
        return "No relevant transcript excerpts were retrieved."

    sections = []

    for index, doc in enumerate(docs, start=1):
        sections.append(
            f"[Transcript excerpt {index}]\n{doc.page_content}"
        )

    return "\n\n---\n\n".join(sections)


def create_rag_chain(retriever):
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an accurate AI meeting assistant.

Answer the user's question using ONLY the meeting transcript
excerpts provided below.

Rules:
1. Answer every part of the user's question.
2. For questions asking for multiple items, identify ALL relevant
   items present in the provided context.
3. Preserve names, responsibilities, deadlines, decisions, and
   unresolved questions accurately.
4. Distinguish confirmed decisions from proposals and open questions.
5. If the transcript says an issue is unresolved, do not invent
   a resolution.
6. Do not use outside knowledge or make unsupported assumptions.
7. If the context does not contain the answer, respond exactly:
   "I could not find this information in the meeting transcript."
8. Be concise, readable, and professional.
9. Use proper spacing and formatting. Do not merge words.
10. When only part of a question can be answered, answer the
    supported part and clearly state what information is missing.

Meeting transcript excerpts:
{context}
"""
        ),
        ("human", "{question}"),
    ])

    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | get_llm()
        | StrOutputParser()
    )

    return rag_chain


def build_rag_chain(transcript: str):
    """Create a vector store from the transcript and build Q&A."""
    if not transcript or not transcript.strip():
        raise ValueError(
            "Cannot build RAG from an empty transcript."
        )

    vector_store = build_vector_store(transcript)
    retriever = get_retriever(vector_store, k=4)

    return create_rag_chain(retriever)


def load_rag_chain():
    """Load the existing persisted vector store for Q&A."""
    vector_store = load_vector_store()
    retriever = get_retriever(vector_store, k=6)

    return create_rag_chain(retriever)


def ask_question(rag_chain, question: str) -> str:
    if not question or not question.strip():
        return "Please enter a question."

    print(f"Question: {question}")

    answer = rag_chain.invoke(question.strip())

    print(f"Answer: {answer}")

    return answer
