# streamlit_app/chat_multimodal.py
# Multimodal Chat: text + per-message PDF/image attachments via a popover next to the chat bar

import os
import base64
from typing import List

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import PyPDF2  # pip install PyPDF2

# ----------------------------
# Setup
# ----------------------------
load_dotenv()
st.set_page_config(page_title="Multimodal Chat (PDF + Image)", page_icon="🤖", layout="centered")

OPENAI_API_KEY = ""
if not OPENAI_API_KEY:
    st.error("Missing OPENAI_API_KEY in your .env file")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# ----------------------------
# Helpers
# ----------------------------
def extract_text_from_pdf(uploaded_pdf) -> str:
    """Extract text from the first few pages of a PDF and soft-cap length."""
    try:
        reader = PyPDF2.PdfReader(uploaded_pdf)
        pages = min(len(reader.pages), 8)  # cap pages to avoid giant prompts
        chunks: List[str] = []
        for i in range(pages):
            text = reader.pages[i].extract_text() or ""
            chunks.append(text)
        doc = "\n".join(chunks).strip()
        # soft cap by characters (token-based capping would be even better)
        return (doc[:8000] + "\n...[truncated]") if len(doc) > 8000 else doc
    except Exception as e:
        return f"[PDF extraction error: {e}]"

def file_to_data_url(file) -> str:
    """Convert an uploaded image file to a base64 data URL for OpenAI image input."""
    data = file.read()
    name = (getattr(file, "name", "") or "").lower()
    mime = "image/png"
    if name.endswith(".jpg") or name.endswith(".jpeg"):
        mime = "image/jpeg"
    elif name.endswith(".png"):
        mime = "image/png"
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:{mime};base64,{b64}"

# ----------------------------
# Session State
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant. If the user uploads files, use them as context."},
        {"role": "assistant", "content": "Hi! Ask anything and use 📎 to attach a PDF or an image to your message."}
    ]

# Buffer for the *current* message's attachments (cleared after send)
if "composer_files" not in st.session_state:
    st.session_state.composer_files = {"pdf": None, "image": None}

# ----------------------------
# Sidebar
# ----------------------------
with st.sidebar:
    st.header("Settings")
    model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"], index=0)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
    max_tokens = st.slider("Max tokens", 128, 4096, 768, 64)
    st.divider()
    if st.button("Clear Chat", type="secondary", use_container_width=True):
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful assistant. If the user uploads files, use them as context."},
            {"role": "assistant", "content": "Chat cleared. Ask a question and attach a PDF or image if you like."}
        ]
        st.session_state.composer_files = {"pdf": None, "image": None}
        st.rerun()

# ----------------------------
# Chat history display
# ----------------------------
st.title("🤖 Multimodal Chat (PDF + Image)")

# Display chat messages
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            # Message content can be a string, or a list (for multimodal 'user' turns)
            if isinstance(msg["content"], list):
                for part in msg["content"]:
                    if part.get("type") == "text":
                        # Only show the original user text, not the PDF content
                        if not part.get("text", "").startswith("[PDF content]"):
                            st.markdown(part.get("text", ""))
                    elif part.get("type") == "image_url":
                        # Don't show images at all, just indicate they were attached
                        st.caption("��️ Image was attached")
            else:
                st.markdown(msg["content"])

# ----------------------------
# Process user input
# ----------------------------
if "user_input" in st.session_state and st.session_state.user_input:
    user_text = st.session_state.user_input
    # Clear the input
    st.session_state.user_input = ""
    
    # Build multimodal 'user' turn for AI processing
    ai_content_parts = []
    if user_text.strip():
        ai_content_parts.append({"type": "text", "text": user_text.strip()})

    # If PDF attached, extract text now and add as a text part (but don't display the text)
    pdf = st.session_state.composer_files["pdf"]
    if pdf is not None:
        pdf_text = extract_text_from_pdf(pdf)
        if pdf_text:
            ai_content_parts.append({"type": "text", "text": f"[PDF content]\n{pdf_text}"})

    # If image attached, convert to data URL and add as image part for AI
    img = st.session_state.composer_files["image"]
    if img is not None:
        data_url = file_to_data_url(img)
        ai_content_parts.append({"type": "image_url", "image_url": {"url": data_url}})

    if not ai_content_parts:
        st.warning("Please type a message or attach a file.")
    else:
        # Create content for chat history (text only, no images)
        history_content_parts = []
        if user_text.strip():
            history_content_parts.append({"type": "text", "text": user_text.strip()})
        if pdf is not None:
            history_content_parts.append({"type": "text", "text": "[PDF content was attached]"})
        if img is not None:
            history_content_parts.append({"type": "text", "text": "[Image was attached]"})

        # Append the user turn to history (text only)
        st.session_state.messages.append({"role": "user", "content": history_content_parts})

        # Display user message (text only, no images)
        with st.chat_message("user"):
            st.markdown(user_text)
            
            # Show attachment indicators
            if pdf is not None:
                st.caption("📄 PDF attached")
            if img is not None:
                st.caption("🖼️ Image attached")

        # Generate AI response using the full content for AI processing
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Create temporary messages with full content for AI
                    temp_messages = st.session_state.messages.copy()
                    temp_messages[-1] = {"role": "user", "content": ai_content_parts}
                    
                    response = client.chat.completions.create(
                        model=model,
                        messages=temp_messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=True
                    )

                    placeholder = st.empty()
                    full = ""
                    for chunk in response:
                        delta = chunk.choices[0].delta
                        if delta and getattr(delta, "content", None):
                            full += delta.content
                            placeholder.markdown(full + "▌")
                    placeholder.markdown(full)

                    st.session_state.messages.append({"role": "assistant", "content": full})
                except Exception as e:
                    st.error(f"Error: {e}")

        # IMPORTANT: clear per-message attachments so they don't leak into the next turn
        st.session_state.composer_files = {"pdf": None, "image": None}

# ----------------------------
# Custom input area at the bottom
# ----------------------------
# Show current attachments as chips
chips = []
if st.session_state.composer_files["pdf"] is not None:
    chips.append("📄 PDF attached")
if st.session_state.composer_files["image"] is not None:
    chips.append("🖼️ Image attached")

if chips:
    st.caption(" • ".join(chips))

# Create columns for input and attachment button
col1, col2 = st.columns([6, 1])

with col1:
    user_text = st.chat_input("Ask a question — attach files via 📎", key="user_input")

with col2:
    # Attachment popover button
    with st.popover("📎", use_container_width=True):
        st.caption("Attach files for this message:")
        st.session_state.composer_files["pdf"] = st.file_uploader(
            "PDF (optional)", type=["pdf"], key="composer_pdf", label_visibility="collapsed"
        )
        st.session_state.composer_files["image"] = st.file_uploader(
            "Image (optional)", type=["png", "jpg", "jpeg"], key="composer_img", label_visibility="collapsed"
        )
        if st.button("Clear attachments"):
            st.session_state.composer_files = {"pdf": None, "image": None}
            st.rerun()
