
import streamlit as st

st.set_page_config(
    page_title="NexaSpeak AI",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "active_page" not in st.session_state:
    st.session_state.active_page = "Home"

st.markdown(
    """
    <style>
    .stApp {
        background: #0b1020;
        color: #f5f7ff;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        max-width: 1000px;
        padding-top: 2rem;
    }

    .brand {
        font-size: 25px;
        font-weight: 700;
        letter-spacing: -1px;
    }

    .brand span {
        color: #a78bfa;
    }

    .eyebrow {
        color: #67e8f9;
        font-size: 12px;
        letter-spacing: 3px;
        text-align: center;
        margin-top: 55px;
    }

    .hero {
        text-align: center;
        font-size: clamp(38px, 6vw, 64px);
        line-height: 1.12;
        font-weight: 750;
        margin: 18px 0;
    }

    .gradient {
        background: linear-gradient(
            90deg, #a78bfa, #67e8f9
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .subtitle {
        text-align: center;
        color: #a4aec5;
        font-size: 16px;
        max-width: 500px;
        margin: auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="brand">✦ NexaSpeak <span>AI</span></div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="eyebrow">YOUR PERSONAL AI ASSISTANT</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        Your ideas,<br>
        <span class="gradient">in every voice.</span>
    </div>
    <div class="subtitle">
        Talk naturally, explore ideas, and turn your
        thoughts into something meaningful.
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

left, center, right = st.columns([1, 1, 1])

with center:
    if st.button("🎙️  Start a conversation", use_container_width=True):
        st.session_state.active_page = "AI Chat"

    if st.button("✧  Ask anything", use_container_width=True):
        st.session_state.active_page = "AI Chat"

    if st.button("▤  Explore knowledge", use_container_width=True):
        st.session_state.active_page = "Knowledge"

st.divider()

st.caption(f"Current section: {st.session_state.active_page}")
