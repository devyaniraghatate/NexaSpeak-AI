import React, { useEffect, useMemo, useState } from "react";
import "./App.css";

const STORAGE_KEY = "nexaspeak_chats_v1";
const USER_KEY = "nexaspeak_demo_user_v1";

function readChats() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
  } catch {
    return [];
  }
}

function makeId() {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function Icon({ name, size = 20 }) {
  const common = {
    width: size, height: size, viewBox: "0 0 24 24", fill: "none",
    stroke: "currentColor", strokeWidth: 1.8, strokeLinecap: "round",
    strokeLinejoin: "round", "aria-hidden": true
  };
  const paths = {
    home: <><path d="m3 10 9-7 9 7"/><path d="M5 9v11h14V9"/><path d="M9 20v-6h6v6"/></>,
    chat: <><path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8A8.5 8.5 0 0 1 8.7 3.9a8.4 8.4 0 0 1 3.8-.9h.5a8.5 8.5 0 0 1 8 8z"/></>,
    history: <><path d="M3 12a9 9 0 1 0 2.6-6.4L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l3 2"/></>,
    plus: <><path d="M12 5v14M5 12h14"/></>,
    send: <><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></>,
    mic: <><rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 10v2a7 7 0 0 0 14 0v-2M12 19v3m-4 0h8"/></>,
    logout: <><path d="M10 17l5-5-5-5"/><path d="M15 12H3"/><path d="M12 3h6a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-6"/></>,
    eye: <><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></>,
    eyeOff: <><path d="m3 3 18 18"/><path d="M10.6 10.6a2 2 0 0 0 2.8 2.8"/><path d="M9.9 5.2A10.7 10.7 0 0 1 12 5c6.5 0 10 7 10 7a16 16 0 0 1-4 4.8"/><path d="M6.2 6.2C3.5 8 2 12 2 12s3.5 7 10 7a10 10 0 0 0 3-.5"/></>,
    spark: <><path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8Z"/><path d="m19 16 .9 2.1L22 19l-2.1.9L19 22l-.9-2.1L16 19l2.1-.9Z"/></>,
    menu: <><path d="M4 6h16M4 12h16M4 18h16"/></>,
    close: <><path d="m18 6-12 12M6 6l12 12"/></>
  };
  return <svg {...common}>{paths[name] || paths.spark}</svg>;
}

function Brand({ small = false }) {
  return <div className={`brand ${small ? "brand-small" : ""}`}>
    <span className="brand-mark"><Icon name="mic" size={small ? 19 : 22} /></span>
    <span>NexaSpeak <b>AI</b></span>
  </div>;
}

function Login({ onLogin }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");

  function submit(e) {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError("Please enter your email and password.");
      return;
    }
    const displayName = name.trim() || email.split("@")[0] || "there";
    const user = { name: displayName, email: email.trim() };
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    onLogin(user);
  }

  return <main className="login-page">
    <div className="login-glow glow-one" /><div className="login-glow glow-two" />
    <section className="login-card">
      <div className="login-brand"><Brand /></div>
      <div className="login-illustration"><div className="orbit orbit-one" /><div className="orbit orbit-two" /><div className="login-orb"><Icon name="spark" size={43} /></div><span className="float-dot dot-a" /><span className="float-dot dot-b" /><span className="float-dot dot-c" /></div>
      <div className="eyebrow">YOUR PERSONAL AI ASSISTANT</div>
      <h1>Ideas start with<br /><span className="gradient-text">a conversation.</span></h1>
      <p className="login-copy">Sign in to chat, explore ideas, and keep your conversations in one place.</p>
      <form onSubmit={submit} className="login-form">
        <label>Your name <span className="optional">(optional)</span></label>
        <input value={name} onChange={e => setName(e.target.value)} placeholder="How should we call you?" autoComplete="name" />
        <label>Email address</label>
        <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" autoComplete="email" required />
        <label>Password</label>
        <div className="password-wrap"><input type={showPassword ? "text" : "password"} value={password} onChange={e => setPassword(e.target.value)} placeholder="Enter your password" autoComplete="current-password" required /><button type="button" className="password-toggle" onClick={() => setShowPassword(v => !v)} aria-label={showPassword ? "Hide password" : "Show password"}><Icon name={showPassword ? "eyeOff" : "eye"} size={19} /></button></div>
        {error && <div className="form-error">{error}</div>}
        <button className="primary-btn login-submit" type="submit">Continue to NexaSpeak <Icon name="send" size={17} /></button>
      </form>
      <div className="demo-note"><span className="status-dot" /> Demo sign-in · No account is created</div>
    </section>
    <footer className="login-footer">NexaSpeak AI <span>·</span> Speak Beyond Limits</footer>
  </main>;
}

function Sidebar({ user, chats, activeId, onSelect, onNew, onLogout, mobileOpen, setMobileOpen }) {
  return <>
    {mobileOpen && <button className="sidebar-scrim" onClick={() => setMobileOpen(false)} aria-label="Close navigation" />}
    <aside className={`sidebar ${mobileOpen ? "sidebar-open" : ""}`}>
      <div className="sidebar-top"><Brand small /><button className="icon-button mobile-close" onClick={() => setMobileOpen(false)} aria-label="Close menu"><Icon name="close" /></button></div>
      <button className="new-chat-btn" onClick={() => { onNew(); setMobileOpen(false); }}><Icon name="plus" size={18} /> New conversation</button>
      <div className="side-label">WORKSPACE</div>
      <button className="side-link selected"><Icon name="chat" /> AI Chat <span className="live-pill">LIVE</span></button>
      <div className="history-heading"><span className="side-label">RECENT CHATS</span><span className="chat-count">{chats.length}</span></div>
      <div className="sidebar-chats">
        {chats.length === 0 ? <div className="empty-sidebar">Your conversations will appear here.</div> : chats.map(chat =>
          <button key={chat.id} className={`history-item ${activeId === chat.id ? "history-active" : ""}`} onClick={() => { onSelect(chat.id); setMobileOpen(false); }}>
            <Icon name="chat" size={16} /><span>{chat.title || "New conversation"}</span>
          </button>
        )}
      </div>
      <div className="sidebar-bottom">
        <div className="user-avatar">{(user.name || "U").slice(0,1).toUpperCase()}</div>
        <div className="user-meta"><strong>{user.name}</strong><span>{user.email}</span></div>
        <button className="icon-button logout-btn" onClick={onLogout} title="Sign out" aria-label="Sign out"><Icon name="logout" size={18} /></button>
      </div>
    </aside>
  </>;
}

function ChatPage({ user, chats, setChats, activeId, setActiveId, onOpenHistory }) {
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const activeChat = chats.find(c => c.id === activeId);
  const messages = activeChat?.messages || [];

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(chats));
  }, [chats]);

  function updateChat(chatId, transform) {
    setChats(prev => prev.map(c => c.id === chatId ? transform(c) : c));
  }

  function startChat() {
    const chat = { id: makeId(), title: "New conversation", createdAt: new Date().toISOString(), updatedAt: new Date().toISOString(), messages: [] };
    setChats(prev => [chat, ...prev]);
    setActiveId(chat.id);
    setInput("");
  }

  function sendMessage(text = input) {
    const value = text.trim();
    if (!value || busy) return;
    let chat = activeChat;
    if (!chat) {
      chat = { id: makeId(), title: value.slice(0, 42), createdAt: new Date().toISOString(), updatedAt: new Date().toISOString(), messages: [] };
      setChats(prev => [chat, ...prev]);
      setActiveId(chat.id);
    }
    const chatId = chat.id;
    const userMessage = { id: makeId(), role: "user", content: value, time: new Date().toISOString() };
    const title = chat.messages.length === 0 ? (value.length > 42 ? value.slice(0, 42) + "…" : value) : chat.title;
    updateChat(chatId, c => ({ ...c, title, updatedAt: new Date().toISOString(), messages: [...c.messages, userMessage] }));
    setInput("");
    setBusy(true);
    window.setTimeout(() => {
      const assistantMessage = {
        id: makeId(), role: "assistant",
        content: "Thanks for your question! This is the NexaSpeak AI interface preview. Connect the Django API and LLM to generate real answers, and connect the RAG pipeline to retrieve information from your documents.",
        time: new Date().toISOString()
      };
      updateChat(chatId, c => ({ ...c, updatedAt: new Date().toISOString(), messages: [...c.messages, assistantMessage] }));
      setBusy(false);
    }, 650);
  }

  function formatTime(iso) {
    try { return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }); } catch { return ""; }
  }

  return <div className="chat-layout">
    <header className="topbar"><div className="topbar-left"><div className="mobile-brand"><Brand small /></div><div className="connection-status"><span className="status-dot" /> UI preview</div></div><button className="history-top-btn" onClick={onOpenHistory}><Icon name="history" size={17} /> Chat history <span>{chats.length}</span></button></header>
    <main className={`chat-main ${messages.length ? "has-messages" : ""}`}>
      {messages.length === 0 ? <div className="welcome">
        <div className="welcome-icon"><Icon name="spark" size={30} /></div>
        <div className="eyebrow">YOUR THOUGHTS, AMPLIFIED</div>
        <h1>Good to see you, {user.name.split(" ")[0] || "there"}.</h1>
        <h2>What can we explore <span className="gradient-text">together?</span></h2>
        <p>Ask a question, brainstorm an idea, or start with one of these prompts.</p>
        <div className="prompt-grid">
          {[
            ["✦", "Explain a complex topic", "Explain RAG in simple terms with an example."],
            ["⌘", "Help me brainstorm", "Give me project ideas for an AI student."],
            ["▤", "Summarize information", "How can a voice assistant use document search?"],
            ["↗", "Plan my day", "Help me make a focused study plan for today."]
          ].map(([icon, title, prompt]) => <button key={title} className="prompt-card" onClick={() => sendMessage(prompt)}><span className="prompt-icon">{icon}</span><strong>{title}</strong><span>{prompt}</span></button>)}
        </div>
      </div> : <div className="messages-wrap">
        <div className="conversation-title"><span className="conversation-icon"><Icon name="chat" /></span><div><strong>{activeChat?.title || "Conversation"}</strong><span>Saved in your chat history</span></div></div>
        {messages.map(msg => <div className={`message-row ${msg.role}`} key={msg.id}>
          <div className={`message-avatar ${msg.role === "assistant" ? "ai-avatar" : ""}`}>{msg.role === "assistant" ? <Icon name="spark" size={17} /> : (user.name || "U").slice(0,1).toUpperCase()}</div>
          <div className="message-content"><div className="message-label">{msg.role === "assistant" ? "NexaSpeak AI" : "You"} <span>{formatTime(msg.time)}</span></div><div className="message-bubble">{msg.content}</div>{msg.role === "assistant" && <div className="message-tools"><button onClick={() => navigator.clipboard?.writeText(msg.content)}>Copy response</button><span>Voice playback can be added with KittenTTS</span></div>}</div>
        </div>)}
        {busy && <div className="message-row assistant"><div className="message-avatar ai-avatar"><Icon name="spark" size={17} /></div><div className="message-content"><div className="message-label">NexaSpeak AI</div><div className="message-bubble typing"><i/><i/><i/></div></div></div>}
        <div className="end-spacer" />
      </div>}
      <div className="composer-area"><form className="composer" onSubmit={e => { e.preventDefault(); sendMessage(); }}><button type="button" className="composer-tool" title="Voice input (not connected)" onClick={() => alert("Voice recording will be connected to Whisper in the next integration step.")}><Icon name="mic" size={20} /></button><textarea rows="1" value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); } }} placeholder="Message NexaSpeak AI..." aria-label="Message NexaSpeak AI" /><button type="submit" className="send-btn" disabled={!input.trim() || busy} aria-label="Send message"><Icon name="send" size={18} /></button></form><div className="composer-note">NexaSpeak AI can make mistakes. Verify important information.</div></div>
    </main>
  </div>;
}

function HistoryPage({ chats, onSelect, onNew, onBack }) {
  const sorted = useMemo(() => [...chats].sort((a,b) => new Date(b.updatedAt) - new Date(a.updatedAt)), [chats]);
  function dateLabel(iso) {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return "Recently";
    const now = new Date();
    return d.toDateString() === now.toDateString() ? "Today" : d.toLocaleDateString([], { month: "short", day: "numeric", year: "numeric" });
  }
  return <div className="history-page"><header className="topbar"><div><div className="eyebrow">YOUR WORKSPACE</div><h2 className="history-page-title">Chat history</h2></div><button className="history-top-btn" onClick={onBack}><Icon name="chat" size={17} /> Back to chat</button></header><div className="history-page-body"><div className="history-intro"><div><h1>Pick up where you left off.</h1><p>Your conversations are saved in this browser on this device.</p></div><button className="primary-btn" onClick={onNew}><Icon name="plus" size={17} /> New chat</button></div>{sorted.length === 0 ? <div className="history-empty"><div className="history-empty-icon"><Icon name="history" size={29}/></div><h3>No conversations yet</h3><p>Start a conversation and it will appear here.</p><button className="primary-btn" onClick={onNew}>Start your first chat</button></div> : <div className="history-list">{sorted.map(chat => <button className="history-card" key={chat.id} onClick={() => onSelect(chat.id)}><div className="history-card-icon"><Icon name="chat" /></div><div className="history-card-main"><strong>{chat.title || "New conversation"}</strong><span>{chat.messages.length} messages · {dateLabel(chat.updatedAt)}</span><p>{chat.messages.filter(m => m.role === "user").slice(-1)[0]?.content || "No messages yet"}</p></div><span className="history-arrow">↗</span></button>)}</div>}</div></div>;
}

export default function App() {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem(USER_KEY) || "null"); } catch { return null; }
  });
  const [chats, setChats] = useState(readChats);
  const [activeId, setActiveId] = useState(() => readChats()[0]?.id || null);
  const [page, setPage] = useState("chat");
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => { localStorage.setItem(STORAGE_KEY, JSON.stringify(chats)); }, [chats]);

  function newChat() {
    const chat = { id: makeId(), title: "New conversation", createdAt: new Date().toISOString(), updatedAt: new Date().toISOString(), messages: [] };
    setChats(prev => [chat, ...prev]);
    setActiveId(chat.id);
    setPage("chat");
  }
  function logout() {
    localStorage.removeItem(USER_KEY);
    setUser(null);
    setPage("chat");
  }
  function selectChat(id) {
    setActiveId(id);
    setPage("chat");
  }

  if (!user) return <Login onLogin={setUser} />;

  return <div className="app-shell">
    <button className="mobile-menu-button" onClick={() => setMobileOpen(true)} aria-label="Open menu"><Icon name="menu" /></button>
    <Sidebar user={user} chats={chats} activeId={activeId} onSelect={selectChat} onNew={newChat} onLogout={logout} mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} />
    <div className="main-panel">
      {page === "chat" ? <ChatPage key={activeId || "empty"} user={user} chats={chats} setChats={setChats} activeId={activeId} setActiveId={setActiveId} onOpenHistory={() => setPage("history")} /> :
       <HistoryPage chats={chats} onSelect={selectChat} onNew={newChat} onBack={() => setPage("chat")} />}
    </div>
  </div>;
}
