import os
from datetime import datetime
from typing import List

import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="NexaSpeak AI", page_icon="🎙️", layout="wide", initial_sidebar_state="expanded")

st.markdown(r'''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root{--bg:#090e1b;--panel:#111a2e;--panel2:#17223a;--border:rgba(148,163,184,.18);--text:#eef3ff;--muted:#9aa9c2;--accent:#8174ff;--cyan:#43d9d2}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}.stApp{background:radial-gradient(ellipse at 75% 0%,rgba(86,75,190,.18),transparent 36%),var(--bg);color:var(--text)}
[data-testid="stHeader"]{background:transparent}.block-container{max-width:1400px;padding-top:1.4rem;padding-bottom:2rem}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#10182a,#0b1221);border-right:1px solid var(--border)}
.nx-brand{display:flex;align-items:center;gap:12px;margin-bottom:1.2rem}.nx-logo{width:48px;height:48px;display:flex;align-items:center;justify-content:center;border-radius:16px;background:linear-gradient(135deg,#8174ff,#42d7d0);font-size:25px;box-shadow:0 8px 30px #5145b555}.nx-brand h1{font-family:'Space Grotesk',sans-serif;font-size:26px;margin:0;color:#f5f7ff}.nx-brand p{margin:3px 0 0;color:var(--muted);font-size:12px}
.nx-hero{padding:27px 30px;border:1px solid var(--border);border-radius:24px;background:linear-gradient(115deg,rgba(124,108,255,.2),rgba(67,217,210,.06) 60%,rgba(255,255,255,.025));margin:6px 0 20px}.nx-eyebrow{color:#a9a0ff;text-transform:uppercase;font-size:11px;font-weight:700;letter-spacing:2px;margin-bottom:10px}.nx-hero h2{font-family:'Space Grotesk',sans-serif;font-size:clamp(28px,3vw,42px);letter-spacing:-1px;line-height:1.13;margin:0 0 12px;color:#f7f8ff}.nx-hero p{color:#b4bfd4;margin:0;max-width:720px;font-size:14px}.nx-chip{display:inline-block;padding:6px 10px;border:1px solid var(--border);border-radius:999px;background:#ffffff08;color:#c5d1e6;font-size:11px;margin:14px 5px 0 0}
.nx-stat{padding:15px 17px;border:1px solid var(--border);background:linear-gradient(145deg,#141e33,#101729);border-radius:16px;min-height:88px}.nx-stat .label{color:var(--muted);font-size:12px}.nx-stat .value{color:#f4f6ff;font-family:'Space Grotesk',sans-serif;font-size:24px;font-weight:700;margin-top:5px}.nx-card{border:1px solid var(--border);border-radius:20px;padding:20px;background:#ffffff04}.nx-muted{color:var(--muted);font-size:12px}.stButton>button{border-radius:12px;border:1px solid var(--border);transition:all .18s ease;font-weight:600;min-height:42px}.stButton>button:hover{border-color:#8174ff;color:#fff;transform:translateY(-1px)}.stButton>button[kind="primary"]{background:linear-gradient(110deg,#7667ff,#4c8de8);border:0;color:white}
[data-testid="stChatMessage"]{border:1px solid var(--border);background:#ffffff05;border-radius:17px;padding:14px 17px;margin-bottom:12px}[data-testid="stChatInput"]{border:1px solid rgba(124,108,255,.45);border-radius:17px;background:#121b2e}[data-testid="stChatInput"] textarea{color:#f4f6ff}[data-testid="stFileUploader"]{border:1px dashed rgba(148,163,184,.3);border-radius:14px;background:#ffffff04;padding:7px}hr{border-color:var(--border)!important}footer,#MainMenu{visibility:hidden}
.nx-login-wrap{max-width:760px;margin:4vh auto 0}.nx-login-card{padding:32px;border:1px solid var(--border);border-radius:26px;background:linear-gradient(145deg,rgba(124,108,255,.13),rgba(17,26,46,.95));box-shadow:0 20px 70px #0003}.nx-login-card h1{font-family:'Space Grotesk',sans-serif;font-size:38px;line-height:1.12;margin:10px 0;color:#f7f8ff}.nx-login-card p{color:#b4bfd4}.nx-feature{border:1px solid var(--border);border-radius:15px;padding:14px;background:#ffffff05;height:100%}
@media(max-width:700px){.block-container{padding:1rem .8rem}.nx-hero{padding:20px}.nx-login-card{padding:20px}.nx-login-card h1{font-size:30px}}
</style>''', unsafe_allow_html=True)

# Session state
for key, default in {
    "logged_in": False, "display_name": "", "messages": [], "last_sources": [],
    "pending_prompt": "", "voice_text": "", "login_error": ""
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

@st.cache_resource(show_spinner=False)
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

def extract_text(file) -> str:
    if file.name.lower().endswith(".pdf"):
        return "\n".join(page.extract_text() or "" for page in PdfReader(file).pages)
    return file.getvalue().decode("utf-8", errors="ignore")

def split_text(text: str, size: int = 850, overlap: int = 120) -> List[str]:
    text = " ".join(text.split())
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text)); chunks.append(text[start:end])
        if end >= len(text): break
        start = end - overlap
    return chunks

def retrieve_context(question, chunks, model, top_k=4):
    if not chunks: return "", []
    vectors = model.encode([c["text"] for c in chunks], convert_to_numpy=True, normalize_embeddings=True)
    q_vector = model.encode([question], convert_to_numpy=True, normalize_embeddings=True)
    scores = cosine_similarity(q_vector, vectors)[0]
    selected = [(chunks[i], float(scores[i])) for i in scores.argsort()[-top_k:][::-1] if scores[i] > .18]
    context = "\n\n".join(f"[Source: {item['source']} | relevance: {score:.2f}]\n{item['text']}" for item, score in selected)
    return context, selected

def do_logout():
    st.session_state.logged_in = False
    st.session_state.display_name = ""
    st.session_state.messages = []
    st.session_state.last_sources = []
    st.rerun()

# LOGIN SCREEN — demo sign-in; not a secure account database
if not st.session_state.logged_in:
    left, right = st.columns([1.08, 1], gap="large", vertical_alignment="center")
    with left:
        st.markdown('<div class="nx-hero"><div class="nx-eyebrow">✦ Your personal AI workspace</div><h2>Speak naturally.<br>Think clearly.</h2><p>Meet NexaSpeak AI — a focused space to ask questions, explore ideas, and chat with your own documents.</p><span class="nx-chip">🎙 Voice-ready</span><span class="nx-chip">📚 Document-aware</span><span class="nx-chip">✦ AI conversation</span></div>', unsafe_allow_html=True)
        a,b,c = st.columns(3)
        for col, icon, title, desc in [(a,"💬","Chat","Ask and follow up"),(b,"🎙️","Speak","Dictate questions"),(c,"📚","Explore","Use your files")]:
            with col: st.markdown(f'<div class="nx-feature"><div style="font-size:25px">{icon}</div><b>{title}</b><div class="nx-muted">{desc}</div></div>',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="nx-login-card"><div class="nx-logo">🎙️</div><div class="nx-eyebrow" style="margin-top:18px">WELCOME TO NEXASPEAK</div><h1>Your ideas,<br>in conversation.</h1><p>Enter your name to open your workspace.</p></div>', unsafe_allow_html=True)
        with st.form("login_form", clear_on_submit=False):
            name = st.text_input("Your name", placeholder="e.g. Devyani")
            st.caption("This demo sign-in opens a session only. It does not create a secure account.")
            submitted = st.form_submit_button("Open my workspace  →", type="primary", use_container_width=True)
            if submitted:
                if name.strip():
                    st.session_state.display_name = name.strip()
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Please enter your name to continue.")
    st.stop()

# Sidebar workspace
with st.sidebar:
    st.markdown(f'<div class="nx-brand"><div class="nx-logo">🎙️</div><div><h1>NexaSpeak AI</h1><p>Welcome, {st.session_state.display_name}</p></div></div>', unsafe_allow_html=True)
    if st.button("＋ New conversation", use_container_width=True, type="primary"):
        st.session_state.messages = []; st.session_state.last_sources = []; st.session_state.voice_text = ""; st.rerun()
    st.divider()
    st.markdown("### ⚙️ Model connection")
    api_base_url = st.text_input("API base URL", value=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"), help="Use your provider's OpenAI-compatible endpoint.")
    api_key = st.text_input("API key", value=os.getenv("OPENAI_API_KEY", ""), type="password", help="Do not share your key.")
    model_name = st.text_input("Chat model", value=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    transcription_model = st.text_input("Transcription model", value=os.getenv("OPENAI_TRANSCRIPTION_MODEL", "whisper-1"))
    if api_key.strip(): st.success("Model key added for this session")
    else: st.info("Add an API key to activate AI and voice transcription.")
    st.divider()
    st.markdown("### 📚 Knowledge library")
    uploaded_files = st.file_uploader("Upload files", type=["pdf", "txt", "md"], accept_multiple_files=True, help="PDF, TXT and Markdown")
    all_chunks = []
    if uploaded_files:
        with st.spinner("Preparing your documents…"):
            for file in uploaded_files:
                try: all_chunks.extend({"source":file.name,"text":chunk} for chunk in split_text(extract_text(file)))
                except Exception as exc: st.warning(f"Could not read {file.name}: {exc}")
        st.caption(f"{len(uploaded_files)} files · {len(all_chunks)} searchable sections")
        with st.expander("View uploaded files"):
            for f in uploaded_files: st.write("📄", f.name)
    st.divider()
    if st.button("Export conversation", use_container_width=True, disabled=not st.session_state.messages):
        export = "\n\n".join(f"{m['role'].title()}: {m['content']}" for m in st.session_state.messages)
        st.download_button("Download .txt", export, file_name="nexaspeak-conversation.txt", mime="text/plain", use_container_width=True)
    if st.button("Sign out", use_container_width=True): do_logout()
    st.caption("Prototype: chats are stored only in the active session, not a database.")

# Main workspace
st.markdown(f'<div class="nx-hero"><div class="nx-eyebrow">✦ YOUR AI WORKSPACE · {datetime.now().strftime("%A, %d %B")}</div><h2>Hi {st.session_state.display_name.split()[0]},<br>what’s on your mind?</h2><p>Type a message or use the microphone below to dictate a question. Upload documents to ask questions grounded in your own material.</p><span class="nx-chip">● Text chat</span><span class="nx-chip">🎙 Record a question</span><span class="nx-chip">⌕ Semantic document search</span></div>', unsafe_allow_html=True)

c1,c2,c3,c4 = st.columns(4)
for col, label, value in [(c1,"Messages",sum(1 for m in st.session_state.messages if m["role"]=="user")),(c2,"Documents",len(uploaded_files or [])),(c3,"Knowledge sections",len(all_chunks)),(c4,"Assistant status","Ready" if api_key.strip() else "Needs API key")]:
    with col: st.markdown(f'<div class="nx-stat"><div class="label">{label}</div><div class="value" style="font-size:{"18px" if isinstance(value,str) else "25px"}">{value}</div></div>',unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("### ✨ Start with a suggestion")
    prompts = [("🧠 Explain a topic","Explain a complex topic in simple terms with an example."),("📄 Summarize files","Summarize the key points from my uploaded documents."),("📝 Make study notes","Create clear study notes from my uploaded documents."),("💡 Brainstorm","Help me brainstorm ideas and organize them into a plan.")]
    cols=st.columns(4)
    for col,(label,prompt) in zip(cols,prompts):
        with col:
            if st.button(label,use_container_width=True,key="prompt_"+label): st.session_state.pending_prompt=prompt; st.rerun()

st.markdown("### 💬 Conversation")
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"]=="user" else "🎙️"):
        st.markdown(message["content"])
if st.session_state.last_sources:
    with st.expander("🔎 Sources used for the latest answer"):
        for item,score in st.session_state.last_sources:
            st.markdown(f"**{item['source']}** · relevance `{score:.2f}`")
            st.caption(item["text"][:350]+("…" if len(item["text"])>350 else ""))

# Voice capture: browser microphone recorder; transcription via configured OpenAI-compatible API
st.markdown("### 🎙️ Speak to NexaSpeak")
st.caption("Tap the recorder, allow microphone access, and record your question. Then click Transcribe and send.")
voice_col, help_col = st.columns([1,2])
with voice_col:
    audio = st.audio_input("Record your question", key="voice_recorder")
with help_col:
    st.markdown('<div class="nx-card"><b>How voice chat works</b><p class="nx-muted">1. Record your question above. 2. Click <b>Transcribe recording</b>. 3. Review the text, then send it to the assistant.</p><p class="nx-muted">Microphone access depends on browser permissions and HTTPS. Voice transcription needs an API key and a compatible transcription endpoint.</p></div>',unsafe_allow_html=True)
if audio:
    if st.button("Transcribe recording", type="primary", key="transcribe_voice"):
        if not api_key.strip(): st.error("Add your API key in Model connection before transcribing.")
        else:
            try:
                client=OpenAI(api_key=api_key.strip(),base_url=api_base_url.strip() or None)
                audio.name = "nexaspeak-question.wav"
                with st.spinner("Transcribing your recording…"):
                    transcript=client.audio.transcriptions.create(model=transcription_model.strip(),file=audio)
                st.session_state.voice_text=transcript.text
                st.rerun()
            except Exception as exc: st.error(f"Transcription failed. Check that your provider supports audio transcription. Details: {exc}")
if st.session_state.voice_text:
    voice_text = st.text_area("Review or edit your transcribed question", value=st.session_state.voice_text, key="voice_text_editor")
    if st.button("Send voice question  ↑", type="primary", use_container_width=True):
        st.session_state.pending_prompt=voice_text.strip(); st.session_state.voice_text=""; st.rerun()

# Main text composer. st.chat_input has an actual submit event and works with Enter.
text_prompt = st.chat_input("Message NexaSpeak AI… (press Enter to send)")
question = text_prompt or st.session_state.pending_prompt
if question:
    st.session_state.pending_prompt = ""
    st.session_state.messages.append({"role":"user","content":question})
    if not api_key.strip():
        answer="Your message was received, but AI responses are not enabled yet. Add a valid model API key in the sidebar, then send your message again."
        st.session_state.messages.append({"role":"assistant","content":answer})
        st.rerun()
    try:
        client_args={"api_key":api_key.strip()}
        if api_base_url.strip(): client_args["base_url"]=api_base_url.strip()
        client=OpenAI(**client_args)
        context=""; sources=[]
        if all_chunks:
            with st.spinner("Searching your documents…"):
                context,sources=retrieve_context(question,all_chunks,load_embedding_model())
        system_prompt="You are NexaSpeak AI, a helpful and clear assistant. Give useful answers with headings or bullets when appropriate. If document context is provided, prioritize it and cite source filenames. If the files do not contain an answer, say so clearly."
        if context: system_prompt += "\n\nRelevant document excerpts:\n"+context
        history=st.session_state.messages[:-1][-10:]
        api_messages=[{"role":"system","content":system_prompt}]+[{"role":m["role"],"content":m["content"]} for m in history]+[{"role":"user","content":question}]
        with st.spinner("NexaSpeak is thinking…"):
            response=client.chat.completions.create(model=model_name.strip(),messages=api_messages,temperature=.45)
        answer=response.choices[0].message.content or "I couldn't generate a response. Please try again."
        st.session_state.messages.append({"role":"assistant","content":answer})
        st.session_state.last_sources=sources
        st.rerun()
    except Exception as exc:
        st.session_state.messages.append({"role":"assistant","content":f"I couldn't complete that request. Check your API key, model name, and base URL.\n\nError details: `{exc}`"})
        st.rerun()

st.markdown('<div style="text-align:center;color:#7786a2;font-size:11px;padding-top:26px">NexaSpeak AI · Interactive prototype · Session-only sign-in and chat</div>',unsafe_allow_html=True)
