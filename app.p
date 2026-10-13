import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { AudioLines, Bot, Check, ChevronDown, CircleHelp, FileText, Headphones, History, Home, LogOut, Menu, Mic, MicOff, MoreHorizontal, Plus, Search, Send, Settings2, Sparkles, SquarePen, Trash2, Upload, UserRound, Volume2, X, Zap } from 'lucide-react';
import './styles.css';

const starters = [
  { icon: FileText, title: 'Summarize a document', text: 'Turn long documents into clear takeaways.' },
  { icon: Sparkles, title: 'Explore an idea', text: 'Think through a question step by step.' },
  { icon: AudioLines, title: 'Talk it out', text: 'Use your voice to start a conversation.' },
];

function App() {
  const [page, setPage] = useState('home');
  const [userName, setUserName] = useState('');
  const [loginName, setLoginName] = useState('');
  const [mobileNav, setMobileNav] = useState(false);
  const [messages, setMessages] = useState([]);
  const [history, setHistory] = useState([]);
  const [input, setInput] = useState('');
  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [uploaded, setUploaded] = useState([]);
  const [showSettings, setShowSettings] = useState(false);
  const [toast, setToast] = useState('');
  const [dark, setDark] = useState(true);
  const bottomRef = useRef(null);
  const fileRef = useRef(null);
  const recognitionRef = useRef(null);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, listening]);
  useEffect(() => { if (toast) { const t = setTimeout(() => setToast(''), 2600); return () => clearTimeout(t); } }, [toast]);
  useEffect(() => () => recognitionRef.current?.stop(), []);

  const notify = (s) => setToast(s);
  const newChat = () => { if (messages.length) setHistory(h => [{ id: Date.now(), title: messages.find(m => m.role === 'user')?.content?.slice(0, 34) || 'New conversation', messages }, ...h]); setMessages([]); setInput(''); setTranscript(''); setPage('home'); setMobileNav(false); };
  const sendMessage = (text = input) => {
    const value = text.trim(); if (!value) return;
    setMessages(prev => [...prev, { role: 'user', content: value }, { role: 'assistant', content: `Thanks for your question! This is the NexaSpeak AI interface prototype. Once the AI backend is connected, I’ll be able to answer “${value}” using your selected model and uploaded knowledge sources.`, demo: true }]);
    setInput(''); setTranscript(''); setPage('chat');
  };
  const toggleMic = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (listening) { recognitionRef.current?.stop(); setListening(false); return; }
    if (!SpeechRecognition) { setTranscript('Voice input is not supported in this browser. Try Chrome and allow microphone access.'); setListening(true); return; }
    const recognition = new SpeechRecognition(); recognition.lang = 'en-IN'; recognition.interimResults = true; recognition.continuous = false;
    recognition.onstart = () => { setListening(true); setTranscript('Listening… speak naturally'); };
    recognition.onresult = (event) => { const text = Array.from(event.results).map(r => r[0].transcript).join(''); setTranscript(text); setInput(text); };
    recognition.onerror = (event) => { setTranscript(event.error === 'not-allowed' ? 'Microphone permission was denied. Allow access in your browser settings.' : 'Could not capture audio. Please try again.'); setListening(false); };
    recognition.onend = () => setListening(false); recognitionRef.current = recognition;
    try { recognition.start(); } catch { setListening(false); notify('Microphone is already active.'); }
  };
  const handleFiles = (e) => { const files = Array.from(e.target.files || []); if (files.length) { setUploaded(old => [...old, ...files.map(f => ({ name: f.name, size: f.size }))]); notify(`${files.length} file${files.length > 1 ? 's' : ''} added to the UI prototype`); } e.target.value = ''; };
  const restoreChat = (item) => { setMessages(item.messages); setPage('chat'); setMobileNav(false); };
  const signIn = (e) => { e.preventDefault(); setUserName(loginName.trim() || 'Guest'); setPage('home'); };

  if (!userName) return <div className={`app-shell ${dark ? 'dark' : 'light'}`}><div className="login-wrap"><div className="login-brand"><div className="brand-mark"><AudioLines size={27}/></div><span>NexaSpeak <b>AI</b></span></div><div className="login-card"><div className="eyebrow"><Sparkles size={14}/> YOUR VOICE-FIRST WORKSPACE</div><h1>Your ideas deserve<br/><span>a conversation.</span></h1><p className="muted">A calm space to think, ask, and explore — with your voice or a message.</p><form onSubmit={signIn}><label htmlFor="name">What should we call you?</label><div className="login-input"><UserRound size={18}/><input id="name" value={loginName} onChange={e => setLoginName(e.target.value)} placeholder="Enter your name" autoFocus /></div><button className="primary-btn full" type="submit">Enter workspace <span>→</span></button></form><div className="login-foot"><span><Check size={14}/> UI prototype</span><span><Zap size={14}/> Voice-first design</span></div></div><p className="login-note">NexaSpeak AI · Your knowledge, in conversation.</p></div></div>;

  return <div className={`app-shell ${dark ? 'dark' : 'light'}`}>
    {mobileNav && <button className="scrim" aria-label="Close navigation" onClick={() => setMobileNav(false)} />}
    <aside className={`sidebar ${mobileNav ? 'open' : ''}`}>
      <div className="sidebar-top"><button className="brand" onClick={() => { setPage('home'); setMobileNav(false); }}><span className="brand-mark"><AudioLines size={23}/></span><span><strong>NexaSpeak <b>AI</b></strong><small>Your knowledge, in conversation.</small></span></button><button className="icon-btn close-nav" onClick={() => setMobileNav(false)} aria-label="Close menu"><X size={19}/></button></div>
      <button className="new-chat" onClick={newChat}><Plus size={17}/> New chat <span className="shortcut">⌘ K</span></button>
      <div className="side-label">WORKSPACE</div>
      <nav className="nav-list">
        <button className={page === 'home' ? 'active' : ''} onClick={() => { setPage('home'); setMobileNav(false); }}><Home size={18}/> Home</button>
        <button className={page === 'chat' ? 'active' : ''} onClick={() => { setPage('chat'); setMobileNav(false); }}><Bot size={18}/> AI Chat</button>
        <button className={page === 'history' ? 'active' : ''} onClick={() => { setPage('history'); setMobileNav(false); }}><History size={18}/> History <span className="nav-count">{history.length}</span></button>
        <button className={page === 'knowledge' ? 'active' : ''} onClick={() => { setPage('knowledge'); setMobileNav(false); }}><FileText size={18}/> Knowledge <span className="nav-count">{uploaded.length}</span></button>
      </nav>
      <div className="side-label recent-label">RECENT CONVERSATIONS</div>
      <div className="history-list">{history.length ? history.slice(0, 7).map(item => <button key={item.id} onClick={() => restoreChat(item)}><span className="history-dot"/>{item.title}</button>) : <p className="empty-side">Your conversations will appear here.</p>}</div>
      <div className="sidebar-bottom"><div className="upgrade-card"><div className="upgrade-icon"><Sparkles size={17}/></div><strong>Make space for ideas</strong><p>Your personal AI workspace, coming to life.</p><button onClick={() => notify('More NexaSpeak features are coming soon.')}>Explore workspace <span>↗</span></button></div><button className="profile" onClick={() => setShowSettings(true)}><span className="avatar">{userName.slice(0,1).toUpperCase()}</span><span className="profile-name"><strong>{userName}</strong><small>Personal workspace</small></span><MoreHorizontal size={19}/></button></div>
    </aside>
    <main className="main-area">
      <header className="topbar"><div className="top-left"><button className="icon-btn mobile-menu" onClick={() => setMobileNav(true)} aria-label="Open navigation"><Menu size={20}/></button><span className="crumb">Workspace <span>/</span> <b>{page === 'home' ? 'Home' : page === 'chat' ? 'AI Chat' : page === 'history' ? 'History' : page === 'knowledge' ? 'Knowledge' : 'Settings'}</b></span></div><div className="top-actions"><span className="status-pill"><i/> UI prototype</span><button className="icon-btn" aria-label="Help" onClick={() => notify('This is the UI-only prototype. Backend integrations come later.')}><CircleHelp size={18}/></button><button className="icon-btn" aria-label="Settings" onClick={() => setShowSettings(true)}><Settings2 size={18}/></button></div></header>
      <div className={`content ${page === 'chat' ? 'chat-content' : ''}`}>
        {page === 'home' && <section className="home-view"><div className="welcome-copy"><div className="eyebrow"><span className="sparkle-dot">✦</span> A LITTLE SPACE FOR BIG IDEAS</div><h1>What’s on your<br className="mobile-break"/> <span>mind today{userName ? `, ${userName}` : ''}?</span></h1><p>Ask a question, speak your thoughts, or explore something new.</p></div><div className="composer home-composer"><textarea value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }} placeholder="Message NexaSpeak AI…" rows={1} aria-label="Message NexaSpeak AI"/><div className="composer-bottom"><div className="composer-tools"><button className="tool-btn" onClick={() => fileRef.current?.click()} aria-label="Attach document"><Plus size={19}/><span>Attach</span></button><button className={`tool-btn mic-tool ${listening ? 'is-listening' : ''}`} onClick={toggleMic}><Mic size={17}/><span>{listening ? 'Listening…' : 'Voice input'}</span></button></div><button className="send-btn" onClick={() => sendMessage()} disabled={!input.trim()} aria-label="Send message"><Send size={17}/></button></div>{listening && <div className="listening-strip"><span className="pulse"><i/></span>{transcript || 'Listening…'}<button onClick={toggleMic}><X size={15}/></button></div>}</div><div className="suggestion-heading"><span>NOT SURE WHERE TO START?</span><span className="suggestion-line"/></div><div className="starter-grid">{starters.map(({icon: Icon, title, text}) => <button className="starter-card" key={title} onClick={() => title === 'Talk it out' ? toggleMic() : setInput(title === 'Summarize a document' ? 'Help me summarize a document.' : 'Help me explore an idea: ')}><span className="starter-icon"><Icon size={19}/></span><strong>{title}</strong><p>{text}</p><span className="card-arrow">↗</span></button>)}</div><div className="home-bottom-note"><span className="mini-spark">✦</span> Thoughtful conversations start with one question.</div></section>}
        {page === 'chat' && <section className="chat-view"><div className="chat-heading"><div><span className="eyebrow">YOUR CONVERSATION</span><h2>{messages.find(m => m.role === 'user')?.content?.slice(0, 48) || 'A fresh conversation'}</h2></div><button className="subtle-btn" onClick={newChat}><SquarePen size={16}/> New chat</button></div><div className="messages">{messages.length === 0 ? <div className="empty-chat"><div className="assistant-orb"><AudioLines size={25}/></div><h3>Let’s start with a question.</h3><p>Type a message or use the microphone to speak.</p></div> : messages.map((m, i) => <article className={`message ${m.role}`} key={i}><div className={`message-avatar ${m.role}`}>{m.role === 'user' ? <UserRound size={17}/> : <AudioLines size={18}/>}</div><div className="message-body"><div className="message-name">{m.role === 'user' ? userName : 'NexaSpeak AI'}{m.demo && <span className="demo-tag">DEMO RESPONSE</span>}</div><p>{m.content}</p>{m.role === 'assistant' && <div className="message-actions"><button onClick={() => { navigator.clipboard?.writeText(m.content); notify('Response copied.'); }}><FileText size={14}/> Copy</button><button onClick={() => notify('Voice playback will be added with the speech engine.')}><Volume2 size={14}/> Listen</button></div>}</div></article>)}<div ref={bottomRef}/></div><div className="chat-compose-wrap"><div className="composer chat-composer"><textarea value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }} placeholder="Message NexaSpeak AI…" rows={1}/><div className="composer-bottom"><div className="composer-tools"><button className="tool-btn" onClick={() => fileRef.current?.click()}><Plus size={18}/><span>Attach</span></button><button className={`tool-btn mic-tool ${listening ? 'is-listening' : ''}`} onClick={toggleMic}><Mic size={17}/><span>{listening ? 'Listening…' : 'Speak'}</span></button></div><button className="send-btn" onClick={() => sendMessage()} disabled={!input.trim()} aria-label="Send message"><Send size={17}/></button></div>{listening && <div className="listening-strip"><span className="pulse"><i/></span>{transcript || 'Listening…'}<button onClick={toggleMic}><X size={15}/></button></div>}</div><p className="disclaimer">NexaSpeak AI is a UI prototype. Responses are placeholders until an AI model is connected.</p></div></section>}
        {page === 'history' && <section className="page-panel"><div className="page-title"><span className="eyebrow">YOUR SPACE</span><h1>Conversation history</h1><p>Pick up where you left off.</p></div><div className="panel-card">{history.length ? history.map(item => <div className="history-row" key={item.id}><div className="history-row-icon"><History size={18}/></div><button onClick={() => restoreChat(item)}><strong>{item.title}</strong><small>{item.messages.length} messages · Saved in this session</small></button><button className="icon-btn" onClick={() => setHistory(h => h.filter(x => x.id !== item.id))} aria-label="Delete conversation"><Trash2 size={16}/></button></div>) : <div className="empty-state"><div className="empty-icon"><History size={22}/></div><h3>No conversations yet</h3><p>Your previous chats will appear here when you start a new one.</p><button className="primary-btn" onClick={newChat}><Plus size={16}/> Start a conversation</button></div>}</div></section>}
        {page === 'knowledge' && <section className="page-panel"><div className="page-title"><span className="eyebrow">YOUR KNOWLEDGE</span><h1>Knowledge library</h1><p>Bring your own material into the conversation.</p></div><div className="upload-drop"><div className="upload-illustration"><Upload size={24}/></div><h3>Add your documents</h3><p>Choose PDF, TXT, or Markdown files. Document understanding will be connected later.</p><button className="primary-btn" onClick={() => fileRef.current?.click()}><Plus size={16}/> Select files</button><small>Files stay in this browser session in the current prototype.</small></div>{uploaded.length > 0 && <div className="panel-card file-list"><div className="file-list-title"><strong>Added this session</strong><span>{uploaded.length} file{uploaded.length !== 1 ? 's' : ''}</span></div>{uploaded.map((f,i) => <div className="file-row" key={i}><div className="file-icon"><FileText size={18}/></div><div className="file-info"><strong>{f.name}</strong><small>{f.size < 1024*1024 ? `${Math.max(1, Math.round(f.size/1024))} KB` : `${(f.size/1024/1024).toFixed(1)} MB`}</small></div><span className="file-status">Added</span><button className="icon-btn" onClick={() => setUploaded(old => old.filter((_,j) => i !== j))} aria-label="Remove file"><X size={16}/></button></div>)}</div>}</section>}
      </div>
      <input ref={fileRef} type="file" multiple accept=".pdf,.txt,.md,.markdown" hidden onChange={handleFiles}/>
      <footer className="footer"><span><span className="footer-dot"/> Made for the way you think.</span><span>NexaSpeak AI <i>·</i> UI/UX prototype</span></footer>
    </main>
    {showSettings && <div className="modal-backdrop" onClick={() => setShowSettings(false)}><div className="settings-modal" onClick={e => e.stopPropagation()}><div className="modal-head"><div><span className="eyebrow">PREFERENCES</span><h2>Workspace settings</h2></div><button className="icon-btn" onClick={() => setShowSettings(false)}><X size={19}/></button></div><div className="setting-row"><div><strong>Appearance</strong><p>Choose your workspace theme.</p></div><button className="theme-toggle" onClick={() => setDark(v => !v)}>{dark ? 'Dark navy' : 'Light'} <ChevronDown size={15}/></button></div><div className="setting-row"><div><strong>Signed in as</strong><p>{userName} · Demo profile</p></div><button className="subtle-btn" onClick={() => { setUserName(''); setLoginName(''); setShowSettings(false); setPage('home'); }}> <LogOut size={15}/> Sign out</button></div><div className="settings-note"><Sparkles size={16}/> AI model, voice synthesis, and cloud sync will be added in a later integration phase.</div></div></div>}
    {toast && <div className="toast"><Check size={16}/>{toast}</div>}
  </div>;
}

createRoot(document.getElementById('root')).render(<App/>);
