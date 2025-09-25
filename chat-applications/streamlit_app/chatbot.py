import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up the page configuration
st.set_page_config(
    page_title="ChatBot",
    page_icon="🤖",
    layout="centered"
)

# Initialize OpenAI client

@st.cache_resource
def init_openai_client():
    api_key = ""
    if not api_key:
        st.error("Please set your OPENAI_API_KEY in a .env file")
        st.stop()
    return OpenAI(api_key=api_key)


client = init_openai_client()

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "assistant",
            "content": "Hello! I'm your AI assistant. How can I help you today?"}
    ]

# App title and description
st.title("🤖 ChatBot")
# st.markdown("A simple chatbot powered by OpenAI's GPT model")

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
                print("Current messages: ", st.session_state.messages)
                # Call OpenAI API
                response = client.chat.completions.create(
                    model=model,
                    messages=st.session_state.messages,  # type: ignore
                    max_completion_tokens=max_tokens,
                    temperature=temperature,
                    stream=True
                )

                # Stream the response
                message_placeholder = st.empty()
                full_response = ""

                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)

                # Add assistant response to chat history
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response})

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error("Please check your OpenAI API key and try again.")
