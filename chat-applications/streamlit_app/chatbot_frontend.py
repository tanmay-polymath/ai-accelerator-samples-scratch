import streamlit as st
import requests
import json

# Set up the page configuration
st.set_page_config(
    page_title="ChatBot with FastAPI",
    page_icon="🤖",
    layout="centered"
)

# FastAPI backend URL
API_BASE_URL = "http://localhost:8000"

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "assistant",
            "content": "Hello! I'm your AI assistant. How can I help you today?"}
    ]

# App title
st.title("🤖 ChatBot with FastAPI Backend")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    model = st.selectbox(
        "Choose Model",
        ["gpt-4o-mini", "gpt-4o"],
        index=0
    )

    max_tokens = st.slider(
        "Max Tokens",
        min_value=50,
        max_value=2000,
        value=500,
        step=50
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1
    )

    if st.button("Clear Chat History"):
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "assistant",
                "content": "Hello! I'm your AI assistant. How can I help you today?"}
        ]
        st.rerun()

# Display chat messages
for message in st.session_state.messages:
    # Don't display system messages in the chat interface
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Prepare request data for FastAPI
                request_data = {
                    "messages": st.session_state.messages,
                    "model": model,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }

                # Call FastAPI backend
                response = requests.post(
                    f"{API_BASE_URL}/chat",
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 200:
                    response_data = response.json()
                    assistant_response = response_data["response"]

                    # Display the response
                    st.markdown(assistant_response)

                    # Add assistant response to chat history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": assistant_response}
                    )
                else:
                    st.error(
                        f"API Error: {response.status_code} - {response.text}")

            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not connect to the FastAPI backend. Make sure it's running on http://localhost:8000")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
