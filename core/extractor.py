
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


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


def build_chain(system_prompt: str):
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Meeting transcript:\n{text}"),
    ])

    return prompt | llm | StrOutputParser()


def extract_action_items(transcript: str) -> str:
    chain = build_chain(
        "You are an accurate meeting analyst. Extract only "
        "explicitly stated or clearly agreed action items. "
        "For each item provide the task, owner, and deadline. "
        "If an owner or deadline is missing, write "
        "'Not specified'. Never invent tasks, owners, or dates. "
        "Return a numbered list. If none exist, return "
        "'No action items found.'"
    )

    return chain.invoke({"text": transcript})


def extract_key_decisions(transcript: str) -> str:
    chain = build_chain(
        "Extract key decisions actually made in the meeting. "
        "Do not confuse suggestions or possibilities with final "
        "decisions. Do not invent information. Return a numbered "
        "list. If none exist, return 'No key decisions found.'"
    )

    return chain.invoke({"text": transcript})


def extract_questions(transcript: str) -> str:
    chain = build_chain(
        "Extract unresolved questions and topics that explicitly "
        "need follow-up. Do not invent questions. Return a "
        "numbered list. If none exist, return "
        "'No open questions found.'"
    )

    return chain.invoke({"text": transcript})
