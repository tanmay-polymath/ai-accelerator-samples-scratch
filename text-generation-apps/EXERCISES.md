# 🔨 Exercises — FastAPI + Streamlit

This set of exercises helps you extend the FastAPI backend and Streamlit frontend to build more capable AI apps.

---

## 1. Enhance FastAPI Backend (Language Support)

- Add a `language` parameter to `/summarize`.
- If set, the backend should **summarize the text and translate it** into the target language.
- Test the new behavior via **Swagger UI** and **cURL**.

---

## 2. Enhance Streamlit App (Language Support)

- Add a **dropdown in the sidebar** for `language` (English, Spanish, French, Hindi, etc.).
- Pass this parameter to the summarization request.
- Verify that the summary is returned in the chosen language.

---

## 3. Image-to-Text Backend

- Extend FastAPI with a new `/describe-image` endpoint.
- Accept an **image upload** (`File` in FastAPI).
- Return a **caption/description** using a vision-capable model.
- Test it using **Swagger** (upload an image).

---

## 4. Connect Streamlit to FastAPI Backend

- Modify the Streamlit summarizer so it **no longer calls OpenAI directly**.
- Instead, send requests to the FastAPI `/summarize` endpoint via **httpx**.
- Benefit: the Streamlit app now works even if the backend model logic changes.

---

## 💡 Suggested Workflow

1. Start with the FastAPI backend enhancements.  
2. Add language support in the Streamlit app.  
3. Try multi-modal input with the image-to-text backend.  
4. Connect both apps together for a clean **frontend ↔ backend architecture**.

---

## ✅ Deliverables

- Updated FastAPI code with `/summarize` (with language parameter) and `/describe-image` endpoints.  
- Updated Streamlit app with language dropdown and backend connection.  
- Screenshots showing successful tests in Swagger, cURL, and Streamlit.  

