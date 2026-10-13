import os
import io
import time
from datetime import datetime
from typing import List

import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="NexaSpeak AI", page_icon="🎙️", layout="wide", initial_sidebar_state="expanded")

# ---------- Styling ----------
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { --nx-bg:#0b1020; --nx-panel:#111a2e; --nx-panel2:#17223a; --nx-border:rgba(148,163,184,.18); --nx-text:#edf3ff; --nx-muted:#9aa9c2; --nx-accent:#7c6cff; --nx-cyan:#43d9d2; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background: radial-gradient(ellipse at 80% 0%, rgba(86,75,190,.18), transparent 35%), var(--nx-bg); color:var(--nx-text); }
[data-testid="stHeader"] { background:transparent; }
.block-container { max-width: 1440px; padding-top: 1.5rem; padding-bottom: 2rem; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#10182a,#0d1424); border-right:1px solid var(--nx-border); }
[data-testid="stSidebar"] .block-container { padding-top:1.5rem; }
.nx-brand { display:flex; align-items:center; gap:13px; margin-bottom:1.2rem; }
.nx-logo { width:48px;height:48px;display:flex;align-items:center;justify-content:center;border-radius:16px;background:linear-gradient(135deg,#8174ff,#42d7d0);font-size:25px;box-shadow:0 8px 30px #5145b555; }
.nx-brand h1 { font-family:'Space Grotesk',sans-serif;font-size:29px;line-height:1.1;margin:0;color:#f5f7ff;letter-spacing:-.8px; }
.nx-brand p { margin:5px 0 0;color:var(--nx-muted);font-size:12px; }
.nx-hero { padding:25px 28px; border:1px solid var(--nx-border); border-radius:24px; background:linear-gradient(115deg,rgba(124,108,255,.19),rgba(67,217,210,.06) 60%,rgba(255,255,255,.025)); margin:8px 0 20px; }
.nx-eyebrow { color:#a9a0ff;text-transform:uppercase;font-size:11px;font-weight:700;letter-spacing:2px;margin-bottom:10px; }
.nx-hero h2 { font-family:'Space Grotesk',sans-serif;font-size:clamp(25px,3vw,37px);letter-spacing:-1px;line-height:1.15;margin:0 0 10px;color:#f7f8ff; }
.nx-hero p { color:#b4bfd4;margin:0;max-width:700px;font-size:14px; }
.nx-chip { display:inline-block;padding:6px 10px;border:1px solid var(--nx-border);border-radius:999px;background:#ffffff08;color:#c5d1e6;font-size:11px;margin:14px 5px 0 0; }
.nx-stat { padding:15px 17px;border:1px solid var(--nx-border);background:linear-gradient(145deg,#141e33,#101729);border-radius:16px;min-height:94px; }
.nx-stat .label { color:var(--nx-muted);font-size:12px; }
.nx-stat .value { color:#f4f6ff;font-family:'Space Grotesk',sans-serif;font-size:25px;font-weight:700;margin-top:4px; }
.nx-section { font-family:'Space Grotesk',sans-serif;font-size:17px;font-weight:600;color:#eff2ff;margin:15px 0 10px; }
.nx-muted { color:var(--nx-muted);font-size:12px; }
.nx-empty { border:1px dashed rgba(148,163,184,.28);border-radius:20px;padding:28px 22px;text-align:center;background:#ffffff03;margin-top:12px; }
.nx-empty .emoji { font-size:35px;margin-bottom:8px; }
.nx-empty h3 { font-family:'Space Grotesk',sans-serif;margin:0 0 8px;font-size:21px;color:#f4f6ff; }
.nx-empty p { color:var(--nx-muted);font-size:13px;margin:0 auto;max-width:540px; }
.stButton > button { border-radius:12px;border:1px solid var(--nx-border);transition:all .18s ease;font-weight:600; }
.stButton > button:hover { border-color:#8174ff;color:#fff;transform:translateY(-1px); }
.stButton > button[kind="primary"] { background:linear-gradient(110deg,#7667ff,#4c8de8);border:0;color:white; }
[data-testid="stChatMessage"] { border:1px solid var(--nx-border);background:#ffffff05;border-radius:17px;padding:14px 17px;margin-bottom:12px; }
[data-testid="stChatInput"] { border:1px solid rgba(124,108,255,.4);border-radius:18px;background:#121b2e; }
[data-testid="stChatInput"] textarea { color:#f4f6ff; }
[data-testid="stFileUploader"] { border:1px dashed rgba(148,163,184,.3);border-radius:14px;background:#ffffff04;padding:7px; }
hr { border-color:var(--nx-border)!important; }
footer { visibility:hidden; }
#MainMenu { visibility:hidden; }
@media (max-width: 700px) { .block-container {padding:1rem .8rem 1.5rem;} .nx-hero {padding:20px;} .nx-brand h1 {font-size:24px;} }
</style>
""", unsafe_allow_html=True)

@st.cache_resource(show_spinner=False)
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


def extract_text(uploaded_file) -> str:
    if uploaded_file.name.lower().endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return uploaded_file.getvalue().decode("utf-8", errors="ignore")


def split_text(text: str, chunk_size: int = 850, overlap: int = 120) -> List[str]:
    text = " ".join(text.split())
    if not text:
        return []
    chunks, start = [], 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def retrieve_context(question: str, chunks: List[dict], model, top_k: int = 4):
    if not chunks:
        return "", []
    texts = [item["text"] for item in chunks]
    vectors = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    q_vector = model.encode([question], convert_to_numpy=True, normalize_embeddings=True)
    scores = cosine_similarity(q_vector, vectors)[0]
    indices = scores.argsort()[-top_k:][::-1]
    selected = [(chunks[i], float(scores[i])) for i in indices if scores[i] > 0.18]
    context = "\n\n".join(f"[Source: {item['source']} | relevance: {score:.2f}]\n{item['text']}" for item, score in selected)
    return context, selected


def reset_chat():
    st.session_state.messages = []
    st.session_state.last_sources = []

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_sources" not in st.session_state:
    st.session_state.last_sources = []
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = ""

# ---------- Sidebar controls ----------
with st.sidebar:
    st.markdown('<div class="nx-brand"><div class="nx-logo">🎙️</div><div><h1 style="font-size:23px">NexaSpeak AI</h1><p>Your knowledge, in conversation.</p></div></div>', unsafe_allow_html=True)
    st.markdown("### ⚙️ Model settings")
    api_base_url = st.text_input("API base URL", value=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"), help="Use your provider's OpenAI-compatible endpoint.")
    api_key = st.text_input("API key", value=os.getenv("OPENAI_API_KEY", ""), type="password", help="Kept in this active app session. Do not share it.")
    model_name = st.text_input("Model name", value=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    connected = bool(api_key.strip() and model_name.strip())
    st.markdown(f'<span class="nx-chip">{"● Model configured" if connected else "○ Add API key to chat"}</span>', unsafe_allow_html=True)
    st.divider()
    st.markdown("### 📚 Knowledge library")
    uploaded_files = st.file_uploader("Add documents to chat with", type=["pdf", "txt", "md"], accept_multiple_files=True, help="PDF, plain text and Markdown files are supported.")
    all_chunks = []
    if uploaded_files:
        with st.spinner("Preparing your knowledge library…"):
            for file in uploaded_files:
                try:
                    content = extract_text(file)
                    all_chunks.extend({"source": file.name, "text": chunk} for chunk in split_text(content))
                except Exception as exc:
                    st.warning(f"Couldn't read {file.name}: {exc}")
        st.success(f"{len(uploaded_files)} file(s) · {len(all_chunks)} searchable sections")
        with st.expander("View uploaded files"):
            for f in uploaded_files:
                st.write(f"📄 {f.name}")
    else:
        st.caption("Upload files to ask questions grounded in your own material.")
    st.divider()
    left, right = st.columns(2)
    with left:
        if st.button("＋ New chat", use_container_width=True):
            reset_chat()
            st.rerun()
    with right:
        if st.button("Export chat", use_container_width=True, disabled=not st.session_state.messages):
            export_text = "\n\n".join(f"{m['role'].title()}: {m['content']}" for m in st.session_state.messages)
            st.download_button("Download .txt", export_text, file_name="nexaspeak-chat.txt", mime="text/plain", use_container_width=True)
    st.caption("Privacy note: this prototype keeps chats in the active session only; it does not use a database.")

# ---------- Main header ----------
st.markdown('<div class="nx-hero"><div class="nx-eyebrow">✦ Your AI workspace</div><h2>Think out loud.<br>Find the signal.</h2><p>Ask questions, explore ideas, and get answers grounded in your uploaded documents — all in one focused workspace.</p><span class="nx-chip">✧ AI chat</span><span class="nx-chip">⌕ Semantic document search</span><span class="nx-chip">↗ Exportable conversations</span></div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f'<div class="nx-stat"><div class="label">Conversation turns</div><div class="value">{sum(1 for m in st.session_state.messages if m["role"] == "user")}</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="nx-stat"><div class="label">Documents added</div><div class="value">{len(uploaded_files or [])}</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="nx-stat"><div class="label">Knowledge sections</div><div class="value">{len(all_chunks)}</div></div>', unsafe_allow_html=True)
with m4:
    st.markdown(f'<div class="nx-stat"><div class="label">Assistant status</div><div class="value" style="font-size:19px">{"Ready" if connected else "Setup needed"}</div></div>', unsafe_allow_html=True)

st.markdown('<div class="nx-section">💬 Your conversation</div>', unsafe_allow_html=True)
if not st.session_state.messages:
    st.markdown('<div class="nx-empty"><div class="emoji">✦</div><h3>What would you like to figure out?</h3><p>Choose a quick start below or type your own question. Upload documents in the sidebar to make answers more relevant to your files.</p></div>', unsafe_allow_html=True)
    st.write("")
    suggestions = [
        ("🧠 Explain a concept", "Explain a complex topic in simple terms with an example."),
        ("📄 Summarize my files", "Summarize the key points from my uploaded documents."),
        ("📝 Create study notes", "Create concise, well-organized study notes from my uploaded documents."),
        ("💡 Brainstorm ideas", "Help me brainstorm useful ideas and organize them into a plan."),
    ]
    suggestion_cols = st.columns(4)
    for col, (label, prompt) in zip(suggestion_cols, suggestions):
        with col:
            if st.button(label, use_container_width=True, key=f"suggest_{label}"):
                st.session_state.pending_prompt = prompt
                st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🎙️"):
        st.markdown(message["content"])

if st.session_state.last_sources and st.session_state.messages:
    with st.expander("🔎 Sources used for the latest answer"):
        for item, score in st.session_state.last_sources:
            st.markdown(f"**{item['source']}** · relevance `{score:.2f}`")
            st.caption(item["text"][:360] + ("…" if len(item["text"]) > 360 else ""))

prompt_from_button = st.session_state.pending_prompt
question = st.chat_input("Message NexaSpeak AI…  (Enter to send)")
if not question and prompt_from_button:
    question = prompt_from_button
    st.session_state.pending_prompt = ""

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(question)
    if not api_key.strip():
        answer = "Your workspace is ready. To enable AI responses, add your model API key in the sidebar. If you use a provider other than OpenAI, enter its compatible API base URL and model name too."
        with st.chat_message("assistant", avatar="🎙️"):
            st.info(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
    else:
        try:
            client_args = {"api_key": api_key.strip()}
            if api_base_url.strip():
                client_args["base_url"] = api_base_url.strip()
            client = OpenAI(**client_args)
            context = ""
            sources = []
            if all_chunks:
                with st.spinner("Searching your documents…"):
                    embedder = load_embedding_model()
                    context, sources = retrieve_context(question, all_chunks, embedder)
            system_prompt = ("You are NexaSpeak AI, a clear, thoughtful assistant. Give structured, useful answers. "
                             "If document context is provided, prioritize it and cite source filenames where possible. "
                             "If the documents do not contain the answer, say so clearly before offering general knowledge.")
            if context:
                system_prompt += "\n\nRelevant document excerpts:\n" + context
            prior_messages = st.session_state.messages[:-1][-10:]
            api_messages = [{"role": "system", "content": system_prompt}]
            api_messages.extend({"role": m["role"], "content": m["content"]} for m in prior_messages)
            api_messages.append({"role": "user", "content": question})
            with st.chat_message("assistant", avatar="🎙️"):
                with st.spinner("NexaSpeak is thinking…"):
                    response = client.chat.completions.create(model=model_name.strip(), messages=api_messages, temperature=0.45)
                    answer = response.choices[0].message.content or "I couldn't generate a response. Please try again."
                st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.session_state.last_sources = sources
        except Exception as exc:
            answer = f"I couldn't complete that request. Check your API key, model name, and base URL.\n\nDetails: `{exc}`"
            with st.chat_message("assistant", avatar="🎙️"):
                st.error(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

st.markdown("<div style='text-align:center;color:#7786a2;font-size:11px;padding-top:26px'>NexaSpeak AI · Prototype workspace · Chats are not saved to a database</div>", unsafe_allow_html=True)
