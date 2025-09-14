# 📝 Text Summarizer (Streamlit + OpenAI)

A tiny, beginner-friendly web app to summarize any text using OpenAI models — built with **Streamlit** and the official **OpenAI** Python SDK.

---

## 🚀 Features
- Paste text → get a clean summary (short / medium / long / custom words)
- Choose model: `gpt-4o-mini` (fast, cheaper) or `gpt-4o` (higher quality)
- Simple UI, minimal code, no streaming (keeps things easy)

---

## 📦 Requirements
- Python 3.9+
- OpenAI API key

Install dependencies:
```bash
pip install -r requirements.txt
```
---

## ▶️ Run the app
```bash
streamlit run app.py
```
Then open the local URL shown in your terminal (usually `http://localhost:8501`).

---

## 🧭 How to use
1. Paste your text into the big text box.
2. Pick a **model**, **summary length**, and **temperature** (lower = more focused).
3. Click **Summarize**.
4. Read / copy the summary shown under “Summary”.

---

## 🗂️ Project structure
```
.
├─ app.py              # Streamlit app
├─ requirements.txt    # Python dependencies
```

---

## ❓ FAQ

**What does `@st.cache_resource` do?**  
It creates the OpenAI client **once** and reuses it across reruns, so the app is faster and cleaner.

**Which model should I pick?**  
- `gpt-4o-mini`: cheaper, faster  
- `gpt-4o`: better quality summaries
