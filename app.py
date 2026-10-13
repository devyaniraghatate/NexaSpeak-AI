import streamlit as st
from datetime import datetime

st.set_page_config(page_title="NexaSpeak AI", page_icon="🎙️", layout="wide", initial_sidebar_state="expanded")

st.markdown(r'''<style>
:root { color-scheme: dark; }
.stApp { background:#212121; color:#ececec; }
[data-testid="stSidebar"] { background:#171717; border-right:1px solid #303030; }
[data-testid="stSidebar"] * { color:#e7e7e7; }
.block-container { max-width: 980px; padding-top: 1.4rem; padding-bottom: 7rem; }
#MainMenu, footer, header { visibility:hidden; }
.brand { display:flex; align-items:center; gap:12px; margin:2px 0 22px; }
.brand-icon { background:linear-gradient(135deg,#7c6cff,#22c7b8); width:42px;height:42px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:23px; }
.brand-name { font-size:20px;font-weight:750;letter-spacing:-.4px; }
.brand-sub { font-size:11px;color:#9ca3af;margin-top:2px; }
.sidebar-label { color:#9ca3af;font-size:12px;text-transform:uppercase;letter-spacing:1px;margin:22px 0 9px; }
.hero { text-align:center; padding:12vh 0 22px; }
.hero h1 { font-size:clamp(30px,4vw,42px); line-height:1.15; letter-spacing:-1.5px; font-weight:650; color:#f7f7f8; }
.hero p { color:#a7a7a7;font-size:15px;margin-top:12px; }
.pill { display:inline-block; border:1px solid #3a3a3a; color:#c8c8c8; border-radius:20px; padding:7px 12px; margin:5px 3px; font-size:12px; }
.chat-row { display:flex; gap:14px; align-items:flex-start; padding:17px 0; border-bottom:1px solid #303030; }
.avatar { flex:0 0 34px; width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px; }
.user-avatar { background:#3a3a3a; } .ai-avatar { background:linear-gradient(135deg,#7567ff,#24bfae); }
.message { line-height:1.65; white-space:pre-wrap; padding-top:4px; color:#ededed; }
.composer-note { color:#888;font-size:11px;text-align:center;margin-top:8px; }
[data-testid="stChatInput"] { border-radius:22px !important; border:1px solid #444 !important; background:#2f2f2f !important; }
[data-testid="stChatInput"] textarea { color:#fff !important; }
.stButton button { border-radius:12px; }
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button { min-height:48px; background:#282828; border:1px solid #3c3c3c; color:#e8e8e8; text-align:left; }
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button:hover { border-color:#777; background:#333; }
.small-muted { color:#8d8d8d;font-size:12px; }
</style>''', unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
if "chats" not in st.session_state: st.session_state.chats = []
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = ""

with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-icon">🎙️</div><div><div class="brand-name">NexaSpeak AI</div><div class="brand-sub">Your knowledge, in conversation.</div></div></div>', unsafe_allow_html=True)
    if not st.session_state.logged_in:
        st.markdown('<div class="sidebar-label">Workspace</div>', unsafe_allow_html=True)
        st.caption("Sign in to personalize this demo workspace.")
        username = st.text_input("Your name", placeholder="Enter your name", label_visibility="collapsed")
        if st.button("Continue to workspace", use_container_width=True, type="primary"):
            st.session_state.username = username.strip() or "Guest"
            st.session_state.logged_in = True
            st.rerun()
        st.markdown('<div class="small-muted">Demo UI only · No account or password is stored.</div>', unsafe_allow_html=True)
    else:
        st.caption(f"Signed in as **{st.session_state.username}** · Demo")
        if st.button("＋  New chat", use_container_width=True):
            if st.session_state.messages:
                st.session_state.chats.insert(0, {"title": next((m["content"][:32] for m in st.session_state.messages if m["role"]=="user"), "New conversation"), "messages": st.session_state.messages.copy()})
            st.session_state.messages = []
            st.rerun()
        st.markdown('<div class="sidebar-label">Recent chats</div>', unsafe_allow_html=True)
        if not st.session_state.chats:
            st.markdown('<div class="small-muted">Your conversations will appear here.</div>', unsafe_allow_html=True)
        for i, chat in enumerate(st.session_state.chats[:8]):
            if st.button("◷  " + chat["title"], key=f"chat_{i}", use_container_width=True):
                st.session_state.messages = chat["messages"].copy()
                st.rerun()
        st.markdown('<div class="sidebar-label">Tools</div>', unsafe_allow_html=True)
        st.file_uploader("Attach a document", type=["pdf", "txt", "md"], help="UI preview only — files are not processed yet.")
        st.markdown('<div class="small-muted">Document analysis will be connected in the backend phase.</div>', unsafe_allow_html=True)
        st.divider()
        if st.button("Sign out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.messages = []
            st.rerun()

st.markdown('<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><span style="font-weight:650;font-size:14px">NexaSpeak AI</span><span class="small-muted">UI preview</span></div>', unsafe_allow_html=True)

if not st.session_state.logged_in:
    st.markdown('''<div class="hero"><div style="font-size:42px;margin-bottom:18px">✦</div><h1>Your ideas, in conversation.</h1><p>A calmer workspace for questions, voice, and knowledge.</p><div style="margin-top:18px"><span class="pill">✦ AI chat interface</span><span class="pill">◉ Voice-ready design</span><span class="pill">▤ Document workspace</span></div></div>''', unsafe_allow_html=True)
    st.info("Enter your name in the sidebar and choose **Continue to workspace** to preview the chat UI.")
else:
    if not st.session_state.messages:
        st.markdown('''<div class="hero"><div style="font-size:36px;margin-bottom:18px">✦</div><h1>What can I help you with?</h1><p>Ask a question, explore an idea, or start with a suggestion.</p></div>''', unsafe_allow_html=True)
        cols = st.columns(2)
        prompts = ["Explain a difficult topic simply", "Help me plan a project", "Summarize a document", "Brainstorm creative ideas"]
        for i, prompt in enumerate(prompts):
            with cols[i % 2]:
                if st.button(prompt, key=f"prompt_{i}", use_container_width=True):
                    st.session_state.pending_prompt = prompt
                    st.rerun()
    for msg in st.session_state.messages:
        is_user = msg["role"] == "user"
        avatar = "🙂" if is_user else "✦"
        cls = "user-avatar" if is_user else "ai-avatar"
        st.markdown(f'<div class="chat-row"><div class="avatar {cls}">{avatar}</div><div class="message">{msg["content"]}</div></div>', unsafe_allow_html=True)
        if not is_user and msg.get("demo"):
            st.caption("Demo response · AI backend not connected")

    prompt = st.chat_input("Message NexaSpeak AI…")
    if "pending_prompt" in st.session_state:
        prompt = st.session_state.pop("pending_prompt")
    if prompt:
        st.session_state.messages.append({"role":"user", "content":prompt})
        response = ("Thanks for your message! This is the NexaSpeak AI UI prototype. The chat layout and interactions are ready to preview; connecting a real AI model will be the next development step.\n\nYour message: “" + prompt + "”")
        st.session_state.messages.append({"role":"assistant", "content":response, "demo":True})
        st.rerun()
    st.markdown('<div class="composer-note">NexaSpeak AI UI prototype · Responses are placeholders for now</div>', unsafe_allow_html=True)

st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
