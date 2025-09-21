# Text Generation Apps — FastAPI Backend + Streamlit UI

This repo demonstrates how to move beyond command-line AI demos and turn them into **usable applications** with:

- **FastAPI** → a backend summarization API (`/summarize`)
- **Streamlit** → a simple summarizer UI app

---

## 📂 Folder Structure

```
.
├── fastapi_service/
│   └── summarizer_api.py    # FastAPI backend
├── streamlit_app/
│   └── summariser_app.py    # Streamlit summarizer app
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

### 1. Pull the latest code and install requirements
```bash
pip install -r requirements.txt
```

---

## 🚀 Running the FastAPI Backend

Start the server:
```bash
uvicorn fastapi_service.summarizer_api:app --reload
```

- API base: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- Health check: `GET /healthz`

### Request Body
The `/summarize` endpoint accepts **JSON** *or* **form-data**:

#### JSON
```json
{
  "text": "Paste your text here...",
  "temperature": 0.3,
  "max_words": 80
}
```

#### Form-data
Fields: `text`, `temperature`, `max_words`

---

## 🧪 Testing the Backend

### 1. Swagger UI
- Open `http://127.0.0.1:8000/docs`
- Expand `POST /summarize`
- Enter valid JSON (use `\n` for newlines)
### 2. Curl

**JSON**
```bash
curl -X POST "http://127.0.0.1:8000/summarize"   -H "Content-Type: application/json"   -d '{"text":"Line 1.\nLine 2.\nLine 3.","temperature":0.3,"max_words":50}'
```

**Form-data**
```bash
curl -X POST "http://127.0.0.1:8000/summarize"   -F "text=Line 1.
Line 2.
Line 3."   -F "temperature=0.3"   -F "max_words=50"
```

### 3. Postman
- Method: **POST**
- URL: `http://127.0.0.1:8000/summarize`
- Choose Body:
  - **raw → JSON** (escape newlines with `\n`)

---

## 🎨 Running the Streamlit App

From the repo root:
```bash
streamlit run streamlit_app/summariser_app.py
```

Opens in your browser at `http://localhost:8501`.

Features:
- Paste text → summarize with OpenAI
- Choose model, temperature, and summary length
- Live token streaming
- Word/character counts + compression ratio

---

## 🛠 Common Issues

- **422 Unprocessable Entity (Swagger JSON)**  
  → Replace raw newlines with `\n` OR use form-data.

- **Port already in use**  
  → Run on a different port:  
  `uvicorn fastapi_service.summarizer_api:app --reload --port 8001`

---

## 📌 Quick Commands Reference

- Run FastAPI:  
  `uvicorn fastapi_service.summarizer_api:app --reload`

- Run Streamlit:  
  `streamlit run streamlit_app/summariser_app.py`
git git
- API Docs:  
  `http://127.0.0.1:8000/docs`

- Health check:  
  `http://127.0.0.1:8000/healthz`
