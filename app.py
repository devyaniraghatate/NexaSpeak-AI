```python
import os
import tempfile
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="NexaSpeak AI",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ NexaSpeak AI")
st.caption("Speak Beyond Limits. Think Beyond Boundaries.")

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "documents" not in st.session_state:
    st.session_state.documents = []

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Settings")

    provider_url = st.text_input(
        "LLM API Base URL",
        value=os.getenv(
            "LLM_API_BASE",
            "https://api.openai.com/v1"
        )
    )

    api_key = st.text_input(
        "LLM API Key",
        value=os.getenv("LLM_API_KEY", ""),
        type="password"
    )

    model_name = st.text_input(
        "Model name",
        value=os.getenv("LLM_MODEL", "")
    )

    st.divider()

    uploaded_files = st.file_uploader(
        "Upload knowledge documents",
        type=["txt", "md", "pdf"],
        accept_multiple_files=True
    )

    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

# ---------------- DOCUMENT READING ----------------
def read_document(uploaded_file):
    filename = uploaded_file.name.lower()

    if filename.endswith((".txt", ".md")):
        return uploaded_file.getvalue().decode(
            "utf-8", errors="ignore"
        )

    if filename.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            import io

            reader = PdfReader(
                io.BytesIO(uploaded_file.getvalue())
            )

            return "\n".join(
                page.extract_text() or ""
                for page in reader.pages
            )
        except Exception as exc:
            st.warning(f"Could not read PDF: {exc}")
            return ""

    return ""


def split_text(text, chunk_size=900, overlap=120):
    text = " ".join(text.split())

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        chunks.append(text[start:start + chunk_size])
        start += chunk_size - overlap

    return chunks


# ---------------- SIMPLE RAG RETRIEVAL ----------------
def retrieve_context(question, chunks, top_k=4):
    """Semantic retrieval using sentence-transformer embeddings."""
    if not chunks:
        return []

    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity

        if "embedder" not in st.session_state:
            st.session_state.embedder = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2"
            )

        embedder = st.session_state.embedder

        chunk_vectors = embedder.encode(
            chunks,
            normalize_embeddings=True
        )

        query_vector = embedder.encode(
            [question],
            normalize_embeddings=True
        )

        scores = cosine_similarity(
            query_vector, chunk_vectors
        )[0]

        indices = scores.argsort()[::-1][:top_k]

        return [
            chunks[i]
            for i in indices
            if scores[i] > 0.15
        ]

    except Exception as exc:
        st.warning(f"Document retrieval unavailable: {exc}")
        return []


# ---------------- LLM RESPONSE ----------------
def generate_answer(question, context):
    if not api_key or not model_name:
        return (
            "The interface is working, but an LLM is not configured. "
            "Enter a valid API key and model name in the sidebar "
            "to generate AI responses."
        )

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=api_key,
            base_url=provider_url
        )

        system_prompt = (
            "You are NexaSpeak AI, a helpful voice assistant. "
            "Answer clearly and accurately. If reference documents "
            "are provided, prioritize them and mention their filenames "
            "when available. If the documents do not contain the answer, "
            "say so instead of inventing information."
        )

        if context:
            system_prompt += (
                "\n\nRelevant document passages:\n"
                + "\n\n".join(context)
            )

        recent_messages = [
            {
                "role": item["role"],
                "content": item["content"]
            }
            for item in st.session_state.messages[-8:]
            if item["role"] in ("user", "assistant")
        ]

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                *recent_messages,
                {"role": "user", "content": question}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as exc:
        return f"Could not generate a response. Check your model settings. Details: {exc}"


# ---------------- PROCESS UPLOADED FILES ----------------
all_chunks = []

if uploaded_files:
    for file in uploaded_files:
        document_text = read_document(file)

        for chunk in split_text(document_text):
            all_chunks.append(
                f"Source: {file.name}\n{chunk}"
            )

    st.sidebar.success(
        f"{len(uploaded_files)} document(s) loaded"
    )

# ---------------- CHAT HISTORY ----------------
st.subheader("💬 Your conversation")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- CHAT INPUT ----------------
question = st.chat_input("Ask NexaSpeak AI anything...")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            context = retrieve_context(question, all_chunks)
            answer = generate_answer(question, context)
            st.markdown(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

# ---------------- OPTIONAL TEXT-TO-SPEECH ----------------
st.divider()
st.subheader("🔊 Voice output")

if st.session_state.messages:
    latest_answer = next(
        (
            m["content"]
            for m in reversed(st.session_state.messages)
            if m["role"] == "assistant"
        ),
        ""
    )

    if st.button("Generate speech for latest answer"):
        try:
            from gtts import gTTS

            audio_file = tempfile.NamedTemporaryFile(
                suffix=".mp3", delete=False
            )

            gTTS(
                text=latest_answer,
                lang="en"
            ).save(audio_file.name)

            with open(audio_file.name, "rb") as audio:
                st.audio(audio.read(), format="audio/mp3")

            os.unlink(audio_file.name)

        except Exception as exc:
            st.error(f"Speech generation failed: {exc}")

st.caption(
    "NexaSpeak AI · Prototype · Verify important AI-generated information."
)
```
