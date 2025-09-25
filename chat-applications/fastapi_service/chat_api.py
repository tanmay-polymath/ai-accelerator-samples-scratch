from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()


def init_openai_client():
    api_key = ""
    if not api_key:
        raise ValueError("Please set your OPENAI_API_KEY in a .env file")
    return OpenAI(api_key=api_key)


client = init_openai_client()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    model: str = "gpt-4o-mini"
    max_tokens: int = 500
    temperature: float = 0.5


@app.get("/")
async def read_root():
    return {"message": "ChatBot API is running"}


@app.post("/chat")
async def chat_completion(request: ChatRequest):
    try:
        # Convert Pydantic models to dict format for OpenAI
        print(request.messages)
        messages_dict = [{"role": msg.role, "content": msg.content}
                         for msg in request.messages]

        response = client.chat.completions.create(
            model=request.model,
            messages=messages_dict,  # type: ignore
            max_completion_tokens=request.max_tokens,
            temperature=request.temperature
        )

        assistant_message = response.choices[0].message.content
        return {"response": assistant_message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
