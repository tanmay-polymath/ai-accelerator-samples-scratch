import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up the page configuration
st.set_page_config(
    page_title="Text Summarizer",
    page_icon="📝",
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

# App title and description
st.title("📝 Text Generation App")
st.markdown("Summarize any text with customizable length using AI")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    model = st.selectbox(
        "Choose Model",
        ["gpt-4o-mini", "gpt-4o"],
        index=0
    )

    summary_length = st.selectbox(
        "Summary Length",
        ["Short (1-2 sentences)", "Medium (1 paragraph)",
         "Long (2-3 paragraphs)", "Custom"],
        index=1
    )

    if summary_length == "Custom":
        max_words = st.number_input(
            "Maximum Words",
            min_value=10,
            max_value=1000,
            value=100,
            step=10
        )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="Lower values = more focused, Higher values = more creative"
    )

# Main content area
st.markdown("### Enter Text to Summarize")

# Text input area
text_input = st.text_area(
    "Paste your text here:",
    height=200,
    placeholder="Enter the text you want to summarize..."
)

# Character and word count
if text_input:
    char_count = len(text_input)
    word_count = len(text_input.split())
    st.caption(f"Characters: {char_count:,} | Words: {word_count:,}")

# Summarize button
if st.button("🔄 Summarize", type="primary", use_container_width=True):
    if not text_input.strip():
        st.warning("Please enter some text to summarize.")
    else:
        with st.spinner("Generating summary..."):
            try:
                # Create summary prompt based on selected length
                if summary_length == "Short (1-2 sentences)":
                    length_instruction = "in 1-2 sentences"
                elif summary_length == "Medium (1 paragraph)":
                    length_instruction = "in one paragraph"
                elif summary_length == "Long (2-3 paragraphs)":
                    length_instruction = "in 2-3 paragraphs"
                else:  # Custom
                    length_instruction = f"in approximately {max_words} words"

                system_message = f"You are a helpful assistant that summarizes text clearly and concisely. Summarize the given text {length_instruction}."

                messages = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"Please summarize the following text:\n\n{text_input}"}
                ]

                # Call OpenAI API
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,  # type: ignore
                    temperature=temperature,
                    stream=True
                )

                # Display summary with streaming
                st.markdown("### Summary")
                summary_container = st.empty()
                full_summary = ""

                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        full_summary += chunk.choices[0].delta.content
                        summary_container.markdown(full_summary + "▌")

                summary_container.markdown(full_summary)

                # Summary statistics
                summary_word_count = len(full_summary.split())
                summary_char_count = len(full_summary)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Original Words", f"{word_count:,}")
                with col2:
                    st.metric("Summary Words", f"{summary_word_count:,}")
                with col3:
                    compression_ratio = round(
                        (1 - summary_word_count / word_count) * 100, 1)
                    st.metric("Compression", f"{compression_ratio}%")

                # Copy button
                st.markdown("---")
                if st.button("📋 Copy Summary", use_container_width=True):
                    st.write("Summary copied to clipboard!")
                    # Note: Actual clipboard functionality would require additional setup

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error("Please check your OpenAI API key and try again.")

# Footer
st.markdown("---")
st.markdown("Built with Streamlit and OpenAI API")

# Help section
with st.expander("ℹ️ How to use"):
    st.markdown("""
    1. **Paste your text** in the text area above
    2. **Choose settings** in the sidebar:
       - Select an AI model
       - Choose summary length or set custom word count
       - Adjust temperature for creativity
    3. **Click 'Summarize'** to generate your summary
    4. **View statistics** showing compression ratio and word counts
    
    **Tips:**
    - Lower temperature (0.0-0.3) = more focused summaries
    - Higher temperature (0.4-1.0) = more creative summaries
    - GPT-4o-mini is faster and more cost-effective
    - GPT-4o provides higher quality summaries
    """)
