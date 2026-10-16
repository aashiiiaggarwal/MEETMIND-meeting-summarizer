
import os
import tempfile
import html
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from utils.audioprocessor import process_input
from core.transcriber import transcribe_all
from core.summarizer import generate_title, summarize
from core.extractor import (
    extract_action_items,
    extract_key_decisions,
    extract_questions,
)
from core.rag_engine import build_rag_chain

load_dotenv()

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MeetMind | AI Meeting Assistant",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# PREMIUM DESIGN SYSTEM
# =========================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #09090F;
    --panel: #11111B;
    --panel-hover: #191827;
    --border: rgba(190, 174, 255, 0.14);
    --text: #F5F2FF;
    --muted: #A19BB8;
    --purple: #A78BFA;
    --purple-dark: #7955F5;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse at 80% 0%,
            rgba(112, 75, 225, .16), transparent 32%),
        radial-gradient(ellipse at 0% 40%,
            rgba(75, 53, 155, .09), transparent 30%),
        var(--bg);
    color: var(--text);
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1200px;
    padding-top: 1.2rem;
    padding-bottom: 3rem;
}

#MainMenu, footer {
    visibility: hidden;
}

h1, h2, h3 {
    font-family: 'Manrope', sans-serif !important;
    color: var(--text) !important;
    letter-spacing: -0.045em;
}

p, li, label {
    color: #D7D2E7;
}

hr {
    border-color: var(--border);
}

.brand {
    display: flex;
    align-items: center;
    gap: 11px;
    font-family: 'Manrope', sans-serif;
    font-size: 1.12rem;
    font-weight: 800;
    letter-spacing: -.04em;
    color: #F8F5FF;
}

.brand-icon {
    display: grid;
    place-items: center;
    width: 34px;
    height: 34px;
    border-radius: 11px;
    color: white;
    background: linear-gradient(140deg, #C4B5FD, #7049EE);
    box-shadow: 0 0 25px rgba(124, 92, 255, .32);
}

.eyebrow {
    color: #B8A5FF;
    font-size: .72rem;
    font-weight: 700;
    letter-spacing: .18em;
    text-transform: uppercase;
}

.hero {
    position: relative;
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 2.2rem;
    background: linear-gradient(
        135deg,
        rgba(29, 26, 48, .97),
        rgba(15, 15, 25, .95)
    );
    animation: fadeUp .65s ease both;
}

.hero:after {
    content: "";
    position: absolute;
    right: -100px;
    top: -170px;
    width: 350px;
    height: 350px;
    border-radius: 50%;
    background: radial-gradient(
        circle, rgba(143, 106, 255, .23), transparent 68%
    );
    pointer-events: none;
}

.hero-title {
    font-family: 'Manrope', sans-serif;
    font-size: clamp(2.3rem, 4.5vw, 3.7rem);
    font-weight: 800;
    line-height: 1.08;
    letter-spacing: -.065em;
    margin: .8rem 0;
    color: #FBF9FF;
}

.gradient-text {
    background: linear-gradient(100deg, #E2D7FF, #A78BFA, #8C7AFF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-copy {
    max-width: 490px;
    color: #A9A3BE;
    font-size: 1rem;
    line-height: 1.8;
}

.pill {
    display: inline-block;
    padding: 6px 10px;
    border: 1px solid rgba(167,139,250,.22);
    border-radius: 30px;
    background: rgba(124,92,255,.10);
    color: #C8B9FF;
    font-size: .70rem;
    font-weight: 600;
    letter-spacing: .04em;
}

.wave-container {
    height: 140px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    margin: .7rem 0;
}

.wave-bar {
    display: block;
    width: 4px;
    height: var(--height);
    border-radius: 8px;
    background: linear-gradient(
        180deg, #E3D9FF, #A78BFA 48%, #6847E8
    );
    box-shadow: 0 0 13px rgba(155, 124, 255, .2);
    animation: waveform var(--duration) ease-in-out
        var(--delay) infinite alternate;
}

.orb {
    position: relative;
    width: 12px;
    height: 12px;
    margin-left: 8px;
    border-radius: 50%;
    background: #E7DCFF;
    box-shadow: 0 0 15px #B9A1FF, 0 0 32px #7955F5;
    animation: pulse 2.2s ease-in-out infinite;
}

.orb:after {
    content: "";
    position: absolute;
    inset: -8px;
    border: 1px solid rgba(180,155,255,.45);
    border-radius: 50%;
    animation: ripple 2.2s ease-out infinite;
}

.feature-card {
    min-height: 128px;
    padding: 1.2rem;
    border: 1px solid var(--border);
    border-radius: 17px;
    background: rgba(18,18,29,.78);
    transition: transform .22s ease,
                border-color .22s ease,
                background .22s ease;
}

.feature-card:hover {
    transform: translateY(-4px);
    border-color: rgba(167,139,250,.45);
    background: var(--panel-hover);
}

.feature-icon {
    color: #BBA8FF;
    font-size: 1.3rem;
    margin-bottom: .7rem;
}

.feature-title {
    font-family: 'Manrope', sans-serif;
    color: #F3EFFF;
    font-weight: 700;
    margin-bottom: .35rem;
}

.feature-copy {
    color: var(--muted);
    font-size: .83rem;
    line-height: 1.6;
}

.section-label {
    margin-bottom: .75rem;
    color: #BDB5D4;
    font-size: .74rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .15em;
}

.meeting-panel {
    padding: 1.3rem;
    border: 1px solid var(--border);
    border-radius: 18px;
    background: rgba(17,17,27,.8);
}

.stTextInput input,
.stTextArea textarea {
    background: #11111B !important;
    color: #F5F2FF !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}

.stButton button,
.stFormSubmitButton button {
    min-height: 2.8rem;
    border: 0;
    border-radius: 12px;
    background: linear-gradient(110deg, #A78BFA, #7955F5);
    color: white;
    font-weight: 700;
    box-shadow: 0 8px 25px rgba(124,92,255,.18);
    transition: transform .2s ease, box-shadow .2s ease;
}

.stButton button:hover,
.stFormSubmitButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(124,92,255,.32);
    color: white;
}

section[data-testid="stFileUploader"] > div {
    background: rgba(17,17,27,.75);
    border: 1px dashed rgba(167,139,250,.42);
    border-radius: 16px;
}

section[data-testid="stFileUploader"] > div:hover {
    border-color: #B8A5FF;
}

div[data-testid="stTabs"] button {
    color: #AAA4BE;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #C8B9FF;
    border-bottom-color: #A78BFA;
}

div[data-testid="stChatMessage"] {
    background: rgba(20,19,32,.85);
    border: 1px solid rgba(185,171,255,.12);
    border-radius: 15px;
    animation: fadeUp .3s ease both;
}

div[data-testid="stExpander"] {
    border: 1px solid var(--border);
    border-radius: 14px;
    background: rgba(18,18,29,.6);
}

.footer {
    margin-top: 3rem;
    padding-top: 1rem;
    text-align: center;
    color: #706A85;
    font-size: .75rem;
}

@keyframes waveform {
    from { transform: scaleY(.35); opacity: .55; }
    to { transform: scaleY(1); opacity: 1; }
}

@keyframes pulse {
    0%, 100% { transform: scale(.85); opacity: .8; }
    50% { transform: scale(1.2); opacity: 1; }
}

@keyframes ripple {
    0% { transform: scale(.65); opacity: .8; }
    100% { transform: scale(1.9); opacity: 0; }
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation: none !important;
        transition: none !important;
    }
}



.result-card {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: 15px 16px;
    margin: 10px 0 5px;
    border: 1px solid rgba(190, 174, 255, 0.12);
    border-radius: 13px;
    background: linear-gradient(
        110deg,
        rgba(31, 28, 49, 0.75),
        rgba(18, 18, 29, 0.7)
    );
    transition: border-color 0.2s ease, transform 0.2s ease;
}

.result-card:hover {
    border-color: rgba(167, 139, 250, 0.38);
    transform: translateX(2px);
}

.result-number {
    display: grid;
    place-items: center;
    flex-shrink: 0;
    width: 29px;
    height: 29px;
    border-radius: 9px;
    background: rgba(167, 139, 250, 0.13);
    color: #C4B5FD;
    font-size: 0.75rem;
    font-weight: 700;
}

.result-body {
    flex: 1;
    min-width: 0;
}

.result-title {
    color: #F0ECFF;
    font-size: 0.94rem;
    font-weight: 600;
    line-height: 1.65;
    overflow-wrap: anywhere;
}

.meeting-panel {
    padding: 1.4rem;
    margin-bottom: 0.5rem;
    border: 1px solid rgba(190, 174, 255, 0.14);
    border-radius: 18px;
    background: rgba(17, 17, 27, 0.82);
}

.meeting-panel p {
    font-size: 0.94rem;
    line-height: 1.85;
    color: #D7D2E7;
    margin-bottom: 0.8rem;
}

.section-label {
    margin-bottom: 1rem;
    color: #BDB5D4;
    font-size: 0.74rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.15em;
}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# UI HELPERS
# =========================================================

def render_waveform():
    heights = [
        22, 34, 48, 27, 57, 78, 43, 29, 55, 84,
        62, 37, 23, 49, 70, 91, 53, 32, 61, 79,
        44, 26, 56, 86, 65, 39, 24, 47, 73, 55,
        31, 63, 82, 46, 28, 51, 74, 40, 22
    ]

    bars = []
    for i, height in enumerate(heights):
        delay = (i % 8) * 0.09
        duration = 0.55 + (i % 5) * 0.13
        bars.append(
            f'<span class="wave-bar" style="--height:{height}px;'
            f'--delay:{delay:.2f}s;--duration:{duration:.2f}s"></span>'
        )

    return (
        '<div class="wave-container">'
        + "".join(bars)
        + '<span class="orb"></span></div>'
    )



def render_section(title, content):
    st.markdown(
        f'<div class="section-label">{html.escape(title)}</div>',
        unsafe_allow_html=True,
    )

    if content is None or content == "":
        st.caption("No information extracted for this section.")
        return

    if isinstance(content, dict):
        content = [content]

    if isinstance(content, (list, tuple)):
        if not content:
            st.caption("No items found.")
            return

        for index, item in enumerate(content, start=1):
            if isinstance(item, dict):
                task = (
                    item.get("task")
                    or item.get("action")
                    or item.get("title")
                    or item.get("description")
                )

                if task:
                    st.markdown(
                        f"""
                        <div class="result-card">
                            <div class="result-number">{index:02d}</div>
                            <div class="result-body">
                                <div class="result-title">
                                    {html.escape(str(task))}
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    details = []
                    for key, value in item.items():
                        if key not in (
                            "task", "action", "title", "description"
                        ) and value:
                            details.append(
                                f"**{key.replace('_', ' ').title()}:** {value}"
                            )

                    if details:
                        st.markdown(
                            "　　" + "　 ·　".join(details)
                        )
                else:
                    st.markdown(
                        "\n".join(
                            f"- **{key.replace('_', ' ').title()}:** {value}"
                            for key, value in item.items()
                        )
                    )

            else:
                st.markdown(
                    f"""
                    <div class="result-card">
                        <div class="result-number">{index:02d}</div>
                        <div class="result-body">
                            <div class="result-title">
                                {html.escape(str(item))}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    else:
        # Keep paragraphs readable when the model returns plain text.
        paragraphs = [
            paragraph.strip()
            for paragraph in str(content).split("\n")
            if paragraph.strip()
        ]

        for paragraph in paragraphs:
            st.markdown(paragraph)


def clear_meeting():
    for key in ("meeting", "chat_history"):
        st.session_state.pop(key, None)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
<div style="display:flex;align-items:center;justify-content:space-between;
            margin:.3rem 0 1.5rem">
    <div class="brand">
        <span class="brand-icon">◉</span>
        MeetMind
    </div>
    <div style="font-size:.72rem;color:#8E88A5;letter-spacing:.1em">
        YOUR PRIVATE MEETING WORKSPACE
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# HOME SCREEN
# =========================================================

if "meeting" not in st.session_state:

    left, right = st.columns([1.08, .92], gap="large")

    with left:
        st.markdown(
            """
<div class="hero">
    <div class="eyebrow">LESS NOTE-TAKING. MORE CLARITY.</div>
    <div class="hero-title">
        Your meeting,<br>
        <span class="gradient-text">understood.</span>
    </div>
    <div class="hero-copy">
        Turn long conversations into clear decisions,
        accountable next steps, and answers you can trust.
    </div>
    <div style="margin-top:1.5rem;display:flex;gap:7px;flex-wrap:wrap">
        <span class="pill">TRANSCRIBE</span>
        <span class="pill">SUMMARIZE</span>
        <span class="pill">ASK ANYTHING</span>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        f1, f2 = st.columns(2, gap="small")

        with f1:
            st.markdown(
                """
<div class="feature-card">
    <div class="feature-icon">✳</div>
    <div class="feature-title">Clear meeting notes</div>
    <div class="feature-copy">
        Summaries, decisions, and unresolved questions in one place.
    </div>
</div>
""",
                unsafe_allow_html=True,
            )

        with f2:
            st.markdown(
                """
<div class="feature-card">
    <div class="feature-icon">↗</div>
    <div class="feature-title">Actionable follow-ups</div>
    <div class="feature-copy">
        Tasks, owners, and deadlines pulled from the conversation.
    </div>
</div>
""",
                unsafe_allow_html=True,
            )

    with right:
        st.markdown(
            f"""
<div class="meeting-panel" style="margin-top:.25rem">
    <div style="display:flex;justify-content:space-between;align-items:center">
        <div class="section-label" style="margin:0">THE MEETING FLOW</div>
        <span class="pill">AI-POWERED</span>
    </div>
    {render_waveform()}
    <div style="text-align:center;font-family:Manrope,sans-serif;
                font-weight:700;font-size:1.15rem;color:#F5F1FF">
        From audio to clarity
    </div>
    <div style="text-align:center;color:#9690AC;font-size:.84rem;
                margin:.45rem 0 1.3rem">
        One recording. Everything that matters.
    </div>
    <div style="display:flex;align-items:center;gap:8px">
        <div style="flex:1;text-align:center;padding:.8rem .3rem;
                    border:1px solid var(--border);border-radius:12px;
                    color:#D5CDEF;font-size:.78rem">
            <span style="color:#A78BFA">01</span><br><b>Transcribe</b>
        </div>
        <span style="color:#8C75E9">→</span>
        <div style="flex:1;text-align:center;padding:.8rem .3rem;
                    border:1px solid var(--border);border-radius:12px;
                    color:#D5CDEF;font-size:.78rem">
            <span style="color:#A78BFA">02</span><br><b>Understand</b>
        </div>
        <span style="color:#8C75E9">→</span>
        <div style="flex:1;text-align:center;padding:.8rem .3rem;
                    border:1px solid var(--border);border-radius:12px;
                    color:#D5CDEF;font-size:.78rem">
            <span style="color:#A78BFA">03</span><br><b>Ask</b>
        </div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">START WITH A RECORDING</div>',
                unsafe_allow_html=True)

    upload_col, url_col = st.columns(2, gap="large")

    with upload_col:
        uploaded_file = st.file_uploader(
            "Upload your meeting audio",
            type=["mp3", "wav", "m4a", "mp4", "mpeg", "mpga", "webm", "ogg", "flac"],
            help="Choose a supported recording from your device.",
        )

    with url_col:
        youtube_url = st.text_input(
            "YouTube recording URL",
            placeholder="Paste a YouTube link…",
        )
        language = st.selectbox(
            "Transcript language",
            ["English", "Hinglish"],
        )

    if uploaded_file and youtube_url.strip():
        st.warning("Please choose an uploaded file OR a YouTube URL.")

    disabled = (
        (not uploaded_file and not youtube_url.strip())
        or (uploaded_file is not None and bool(youtube_url.strip()))
    )

    process_clicked = st.button(
        "✦  Create meeting notes",
        type="primary",
        use_container_width=True,
        disabled=disabled,
    )

    if process_clicked:
        temp_path = None
        source = youtube_url.strip()

        try:
            if uploaded_file:
                suffix = Path(uploaded_file.name).suffix or ".mp3"

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix,
                ) as temp_file:
                    temp_file.write(uploaded_file.getbuffer())
                    temp_path = temp_file.name

                source = temp_path

            with st.status(
                "Turning your recording into meeting notes…",
                expanded=True,
            ) as status:
                st.write("Preparing your audio…")
                chunks = process_input(source)

                st.write("Transcribing the conversation…")
                transcript = transcribe_all(
                    chunks,
                    language=language.lower(),
                )

                if not transcript or not transcript.strip():
                    raise ValueError(
                        "No transcript was generated. "
                        "Try a clearer recording."
                    )

                st.write("Generating meeting notes with Gemini…")
                title = generate_title(transcript)
                summary = summarize(transcript)
                action_items = extract_action_items(transcript)
                decisions = extract_key_decisions(transcript)
                questions = extract_questions(transcript)

                st.write("Preparing meeting-aware Q&A…")
                rag_chain = build_rag_chain(transcript)

                status.update(
                    label="Your meeting is ready!",
                    state="complete",
                    expanded=False,
                )

            st.session_state.meeting = {
                "title": title,
                "summary": summary,
                "action_items": action_items,
                "decisions": decisions,
                "questions": questions,
                "transcript": transcript,
                "rag_chain": rag_chain,
                "source_name": (
                    uploaded_file.name
                    if uploaded_file
                    else "YouTube recording"
                ),
            }
            st.session_state.chat_history = []
            st.rerun()

        except Exception as exc:
            st.error(f"Couldn't process this recording: {exc}")
            st.caption(
                "Check your .env API keys, supported audio format, "
                "and backend function names."
            )

        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass


# =========================================================
# MEETING WORKSPACE
# =========================================================

else:
    meeting = st.session_state.meeting
    title = html.escape(str(meeting.get("title") or "Meeting notes"))

    st.markdown(
        f"""
<div style="margin:.7rem 0 1.3rem">
    <div class="eyebrow">YOUR MEETING WORKSPACE</div>
    <div class="hero-title" style="font-size:clamp(1.8rem,3.5vw,2.8rem);
                                   margin:.5rem 0">
        {title}
    </div>
    <div style="color:#9F99B5;font-size:.84rem">
        <span style="color:#B19AFF">●</span>
        {html.escape(str(meeting.get('source_name', 'Meeting recording')))}
        &nbsp; · &nbsp; Transcript ready
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    top_left, top_right = st.columns([1, 5])

    with top_left:
        if st.button("← New meeting", use_container_width=True):
            clear_meeting()
            st.rerun()

    notes_tab, chat_tab, transcript_tab = st.tabs(
        ["✦  Meeting notes", "◉  Ask your meeting", "≡  Transcript"]
    )

    with notes_tab:
        st.markdown('<div class="meeting-panel">', unsafe_allow_html=True)
        render_section("Overview", meeting.get("summary"))
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        left, right = st.columns(2, gap="large")

        with left:
            st.markdown(
                '<div class="meeting-panel">',
                unsafe_allow_html=True,
            )
            render_section("↗  Action items", meeting.get("action_items"))
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown(
                '<div class="meeting-panel">',
                unsafe_allow_html=True,
            )
            render_section("✦  Key decisions", meeting.get("decisions"))
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        st.markdown(
            '<div class="meeting-panel">',
            unsafe_allow_html=True,
        )
        render_section("Open questions", meeting.get("questions"))
        st.markdown("</div>", unsafe_allow_html=True)

    with chat_tab:
        st.markdown(
            '<div class="section-label">MEETING-AWARE ASSISTANT</div>',
            unsafe_allow_html=True,
        )
        st.write(
            "Ask about decisions, deadlines, owners, risks, "
            "or anything discussed in this meeting."
        )

        for message in st.session_state.get("chat_history", []):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        prompt = st.chat_input("Ask a question about this meeting…")

        if prompt:
            st.session_state.chat_history.append(
                {"role": "user", "content": prompt}
            )

            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Finding the relevant context…"):
                    try:
                        # Use the existing RAG chain directly.
                        answer = meeting["rag_chain"].invoke(prompt)
                    except Exception as exc:
                        answer = f"Sorry, I couldn't answer that: {exc}"

                st.markdown(answer)

            st.session_state.chat_history.append(
                {"role": "assistant", "content": answer}
            )

    with transcript_tab:
        st.markdown(
            '<div class="section-label">SOURCE TRANSCRIPT</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Review the original transcript to verify names and details."
        )
        st.text_area(
            "Transcript",
            value=meeting.get("transcript", ""),
            height=480,
            label_visibility="collapsed",
        )


st.markdown(
    '<div class="footer">MeetMind · Made for clearer conversations</div>',
    unsafe_allow_html=True,
)
