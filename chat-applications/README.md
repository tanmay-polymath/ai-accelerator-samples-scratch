# 🤖 Text Generation Apps — Chatbots with FastAPI Backend + Streamlit UI

This repo demonstrates how to move beyond command-line AI demos and turn them into **usable chatbot applications** with:

- **FastAPI** → a backend chat API (`/chat`)  
- **Streamlit** → chat UIs ranging from simple to advanced (with PDF support)

---

## 📂 Folder Structure

```
.
├── fastapi_service/
│   └── chat_api.py           # FastAPI backend for chat
├── streamlit_app/
│   ├── chatbot.py            # Basic chatbot (Streamlit-only, calls OpenAI directly)
│   ├── chatbot_frontend.py   # Streamlit frontend that calls FastAPI /chat
│   └── chatbot_advanced.py        # Advanced chatbot with PDF support
├── requirements.txt          # Shared dependencies
├── EXERCISES.md              # Workshop exercises
└── README.md                 # Setup + usage guide
```

---

## ⚙️ Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```
---

## 🚀 Running the FastAPI Backend

Start the server:
```bash
uvicorn fastapi_service.chat_api:app --reload
```

- API base: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`

### Example Request Body
The `/chat` endpoint accepts JSON with messages:

```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the weather in Dallas?"}
  ]
}
```

---

## 🧪 Testing the Backend

### 1. Swagger UI
- Open `http://127.0.0.1:8000/docs`
- Expand `POST /chat`
- Add sample JSON (see above)

### 2. Curl
```bash
curl -X POST "http://127.0.0.1:8000/chat"   -H "Content-Type: application/json"   -d '{"messages":[{"role":"user","content":"Hello!"}]}'
```

### 3. Postman
- Method: **POST**
- URL: `http://127.0.0.1:8000/chat`
- Body → raw JSON → add messages array

---

## 🎨 Running the Streamlit Apps

### 1. Basic Chatbot
```bash
streamlit chatbot.py
```
Features:
- Simple chatbot UI with streaming
- Session state for memory

---

### 2. Streamlit Frontend (FastAPI Backend)
```bash
streamlit run chatbot_frontend.py
```
Features:
- Frontend calls the FastAPI `/chat` endpoint
- Realistic client-server separation
- Easy to swap in different backends

---

### 3. Advanced Chatbot (Multimodal)
```bash
streamlit run chatbot_advanced.py
```
Features:
- Supports PDF (and image) inputs
- Chat context includes extracted text
- Useful for document Q&A demos

---

## 🛠 Common Issues

- **422 Unprocessable Entity**  
  → Ensure JSON body matches the schema (`messages` must be a list of objects).  

- **Port already in use**  
  → Run on another port:  
  `uvicorn fastapi_service.chat_api:app --reload --port 8001`  

---

## 📌 Quick Commands Reference

- Run FastAPI:  
  ```bash
  uvicorn chat_api:app --reload
  ```

- Run Basic Chatbot (Streamlit-only):  
  ```bash
  streamlit run chatbot.py
  ```

- Run Streamlit + FastAPI frontend:  
  ```bash
  streamlit run chatbot_frontend.py
  ```

- Run Advanced Chatbot:  
  ```bash
  streamlit run chatbot_advanced.py
  ```

- API Docs:  
  `http://127.0.0.1:8000/docs`

- Health check:  
  `http://127.0.0.1:8000/healthz`

---

Happy coding! 🚀
