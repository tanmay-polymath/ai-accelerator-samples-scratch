# Import required libraries
from fastapi import FastAPI          # FastAPI framework for building APIs
from pydantic import BaseModel       # For defining request/response data shapes
from openai import OpenAI            # OpenAI client
import os
from dotenv import load_dotenv       # To load API keys from a .env file

# ----------------------------
# 1. Setup
# ----------------------------

# Load environment variables from the .env file (must contain OPENAI_API_KEY)
load_dotenv()

# Initialize OpenAI client using the API key
client = OpenAI(api_key="")

# Create the FastAPI app
app = FastAPI(
    title="Summarizer API",
    version="1.0",
    description="A simple API that summarizes text using OpenAI models."
)

# ----------------------------
# 2. Define data models
# ----------------------------

# Request body schema: what the client must send
class SummarizeRequest(BaseModel):
    text: str                    # The text to summarize
    temperature: float = 0.3     # Controls creativity (0 = focused, 1 = creative)
    max_words: int = 100         # Maximum number of words in the summary

# Response schema: what the API will return
class SummarizeResponse(BaseModel):
    summary: str                 # The generated summary text
    word_count: int              # Number of words in the summary

# ----------------------------
# 3. Health check endpoint
# ----------------------------

@app.get("/healthz")
def health_check():
    """
    Simple check to see if the API is running.
    Returns {"status": "ok"} when the service is up.
    """
    return {"status": "ok"}

# ----------------------------
# 4. Summarization endpoint
# ----------------------------

@app.post("/summarize", response_model=SummarizeResponse)
def summarize(req: SummarizeRequest):
    """
    Summarize the given text using OpenAI API.

    Inputs:
      - text: the text to summarize
      - temperature: how creative the summary should be (0.0 - 1.0)
      - max_words: approximate length of the summary

    Output:
      - summary: the summarized text
      - word_count: number of words in the summary
    """

    # Guard clause: return empty if no text is provided
    if not req.text.strip():
        return {"summary": "", "word_count": 0}

    # Create the system instruction for the AI
    system_message = f"You are a helpful assistant that summarizes text in about {req.max_words} words."

    # Build the conversation: system + user
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": req.text}
    ]

    # Call the OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",       # You can also try "gpt-4o"
        messages=messages,
        temperature=req.temperature
    )

    # Extract the summary text from the response
    summary = response.choices[0].message.content.strip()

    # Return both summary and word count
    return {"summary": summary, "word_count": len(summary.split())}
