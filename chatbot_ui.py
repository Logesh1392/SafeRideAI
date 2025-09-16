import os
import streamlit as st
import faiss
import numpy as np
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from db_utils import get_db_connection
from chat_report import save_chat_report

# -----------------------------
# Fetch recent detections
# -----------------------------
def fetch_recent_detections(limit=500):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, class, confidence, file_name, created_at
            FROM detections
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (limit,)
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        st.error(f"DB Error: {e}")
        return []

# -----------------------------
# Load embedding model
# -----------------------------
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

embedding_model = load_embedding_model()

# -----------------------------
# Build FAISS index
# -----------------------------
@st.cache_resource
def build_faiss_index():
    detections = fetch_recent_detections(500)
    texts = [f"{r[1]} ({r[2]*100:.1f}%) in {r[3]} at {r[4]}" for r in detections]

    if texts:
        vectors = embedding_model.encode(texts, convert_to_numpy=True)
        dim = vectors.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(vectors)
    else:
        index = None
        vectors = np.array([])

    return index, texts, detections

faiss_index, faiss_texts, faiss_metadata = build_faiss_index()

# -----------------------------
# Groq LLM Client
# -----------------------------
llm_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# -----------------------------
# Streamlit Chatbot UI
# -----------------------------
def chatbot_ui():  
    st.set_page_config(page_title="SafeRideAI Chatbot", layout="wide")
    st.title("🛡️ SafeRideAI Assistant")
    st.subheader("Ask questions about helmet & accident detections or chat freely")

    # -----------------------------
    # Initialize session state
    # -----------------------------
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # -----------------------------
    # Input: Search box + buttons (vertical)
    # -----------------------------
    with st.form(key="chat_form", clear_on_submit=True):
        user_query_input = st.text_input(
            "💬 Ask me anything about detections or chat:",
            key="search_box",
            placeholder="Type your question here..."
        )
        send_btn = st.form_submit_button("Send")
        clear_btn = st.form_submit_button("🧹 Clear History")

        if clear_btn:
            st.session_state.chat_history = []

    # -----------------------------
    # Refresh FAISS index periodically
    # -----------------------------
    def refresh_faiss_if_needed(interval_minutes=2):
        last_update = st.session_state.get("faiss_last_update", datetime.min)
        if datetime.now() - last_update > timedelta(minutes=interval_minutes):
            index, texts, metadata = build_faiss_index()
            st.session_state.faiss_index = index
            st.session_state.faiss_texts = texts
            st.session_state.faiss_metadata = metadata
            st.session_state.faiss_last_update = datetime.now()

    if "faiss_index" not in st.session_state:
        st.session_state.faiss_index = faiss_index
        st.session_state.faiss_texts = faiss_texts
        st.session_state.faiss_metadata = faiss_metadata
        st.session_state.faiss_last_update = datetime.now()

    refresh_faiss_if_needed(interval_minutes=2)

    # -----------------------------
    # Handle query submission
    # -----------------------------
    if user_query_input and send_btn:
        user_query = user_query_input

        # Determine RAG mode
        RAG_KEYWORDS = ["helmet", "accident", "detection", "ride", "crash", "logs", "safety"]
        use_rag = any(word in user_query.lower() for word in RAG_KEYWORDS)

        retrieved_texts = ""
        if use_rag:
            index = st.session_state.faiss_index
            texts = st.session_state.faiss_texts
            if index and len(texts) > 0:
                q_vec = embedding_model.encode([user_query], convert_to_numpy=True)
                k = min(5, len(texts))
                D, I = index.search(q_vec, k=k)
                for idx in I[0]:
                    retrieved_texts += texts[idx] + "\n"

            recent_detections = fetch_recent_detections(10)
            db_summary = ""
            for r in recent_detections:
                db_summary += f"- {r[1]} ({r[2]*100:.1f}%) in {r[3]} at {r[4]}\n"

            messages = [
                {"role": "system", "content": "You are SafeRideAI assistant. Answer queries about helmet/accident detections in a friendly, helpful tone."},
                *st.session_state.chat_history,
                {"role": "user", "content": f"{user_query}\n\nSemantic matches:\n{retrieved_texts}\nRecent structured DB logs:\n{db_summary}"}
            ]
        else:
            messages = [
                {"role": "system", "content": "You are SafeRideAI assistant. Answer in a friendly, conversational way."},
                *st.session_state.chat_history,
                {"role": "user", "content": user_query}
            ]

        # Call LLM
        response = llm_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )
        bot_reply = response.choices[0].message.content

        # Emoji hints
        if use_rag:
            if "accident" in bot_reply.lower():
                bot_reply = "🚨 " + bot_reply
            elif "helmet" in bot_reply.lower():
                bot_reply = "🪖 " + bot_reply
            elif "no" in bot_reply.lower() or "none" in bot_reply.lower() or "zero" in bot_reply.lower():
                bot_reply = "✅ " + bot_reply

        # Update chat history
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

    # -----------------------------
    # Display chat history
    # -----------------------------
    for msg in reversed(st.session_state.chat_history):
        if msg["role"] == "user":
            st.markdown(
                f"<div style='background-color:#DCF8C6; padding:8px; border-radius:10px; margin:5px 0; text-align:right;'>🧑 {msg['content']}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div style='background-color:#E6E6FA; padding:8px; border-radius:10px; margin:5px 0; text-align:left;'>🤖 {msg['content']}</div>",
                unsafe_allow_html=True
            )

    # -----------------------------
    # PDF Export Section
    # -----------------------------
    st.subheader("📑 Chat Report")
    if st.button("Generate Chat Report PDF"):
        if st.session_state.chat_history:
            pdf_file = save_chat_report(st.session_state.chat_history)
            st.download_button(
                label="⬇️ Download Chat Report",
                data=pdf_file,
                file_name="chat_report.pdf",
                mime="application/pdf",
            )
        else:
            st.warning("No chat history available to export.")
