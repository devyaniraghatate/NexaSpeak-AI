import os
import tempfile
from typing import List

import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="NexaSpeak AI", page_icon="🎙️", layout="wide")

st.title("🎙️ NexaSpeak AI")
st.caption("A document-aware AI assistant. Add an API-compatible language model to enable answers.")

# Cache the embedding model so it is not downloaded again on every rerun.
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


def extract_text(uploaded_file) -> str:
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return uploaded_file.getvalue().decode("utf-8", errors="ignore")


def split_text(text: str, chunk_size: int = 900, overlap: int = 150) -> List[str]:
    text = " ".join(text.split())
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def retrieve_context(question: str, chunks: List[str], model, top_k: int = 3) -> str:
    if not chunks:
        return ""
    vectors = model.encode(chunks, convert_to_numpy=True)
    question_vector = model.encode([question], convert_to_numpy=True)
    scores = cosine_similarity(question_vector, vectors)[0]
    best_indices = scores.argsort()[-top_k:][::-1]
    return "\n\n".join(chunks[i] for i in best_indices if scores[i] > 0.15)


with st.sidebar:
    st.header("Settings")
    api_base_url = st.text_input(
        "API base URL (optional)",
        value=os.getenv("OPENAI_BASE_URL", ""),
        placeholder="https://api.openai.com/v1",
        help="Use your provider's OpenAI-compatible API endpoint. Leave blank for the default OpenAI endpoint.",
    )
    api_key = st.text_input(
        "API key",
        value=os.getenv("OPENAI_API_KEY", ""),
        type="password",
        help="Your key is used for this app session. Do not share it publicly.",
    )
    model_name = st.text_input(
        "Model name",
        value=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    )
    st.divider()
    st.subheader("Knowledge documents")
    uploaded_files = st.file_uploader(
        "Upload PDF, TXT, or Markdown files",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
    )

all_chunks = []
if uploaded_files:
    with st.spinner("Reading your documents..."):
        for file in uploaded_files:
            extracted = extract_text(file)
            all_chunks.extend([f"Source: {file.name}\n{chunk}" for chunk in split_text(extracted)])
    st.sidebar.success(f"Loaded {len(uploaded_files)} file(s), {len(all_chunks)} text chunk(s).")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    if st.button("Clear current chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.caption("Chat history is kept only for this active session; it is not stored in a database.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask NexaSpeak AI a question...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    if not api_key.strip():
        answer = "Please add your API key in the sidebar to enable AI responses. You can upload documents first, then ask questions after configuring the model."
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
    else:
        try:
            client_args = {"api_key": api_key.strip()}
            if api_base_url.strip():
                client_args["base_url"] = api_base_url.strip()
            client = OpenAI(**client_args)

            context = ""
            if all_chunks:
                with st.spinner("Searching your documents..."):
                    embedder = load_embedding_model()
                    context = retrieve_context(question, all_chunks, embedder)

            system_prompt = (
                "You are NexaSpeak AI, a clear and helpful assistant. "
                "If document context is provided, use it when relevant. "
                "If the context does not contain the answer, say so and then distinguish any general knowledge."
            )
            if context:
                system_prompt += "\n\nRelevant document context:\n" + context

            # Exclude the current question from history here because it is sent separately below.
            prior_messages = st.session_state.messages[:-1][-10:]
            api_messages = [{"role": "system", "content": system_prompt}]
            api_messages.extend(
                {"role": m["role"], "content": m["content"]} for m in prior_messages
            )
            api_messages.append({"role": "user", "content": question})

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = client.chat.completions.create(
                        model=model_name.strip(),
                        messages=api_messages,
                        temperature=0.4,
                    )
                    answer = response.choices[0].message.content or "I couldn't generate a response. Please try again."
                st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

        except Exception as exc:
            answer = f"The AI request failed: {exc}\n\nCheck your API key, model name, and API base URL in the sidebar."
            with st.chat_message("assistant"):
                st.error(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

st.divider()
st.caption("Prototype note: this version supports text chat and document retrieval. Microphone transcription, KittenTTS voice output, persistent accounts, and database-backed chat history are not included yet.")
