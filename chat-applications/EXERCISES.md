# 📝 Exercises — Chatbot Extensions

This set of exercises helps you extend the FastAPI backend and Streamlit frontend to build more capable **retail-focused AI chatbots**.

---

## 1. Persona Selector

- Add a dropdown in the sidebar to choose a chatbot persona.  
- Example personas: *Therapist, Primary School Teacher, Customer Service Agent*. You can choose and add your own.  
- ✅ System message updates and assistant’s tone changes accordingly.  

---

## 2. Context Management (Truncate + Summarized Memory)

- **Part A:** Truncate chat history to keep only the last 5 turns.  
- **Part B:** Instead of dropping old turns, summarize them into a compressed memory, and keep the summary of the older chats plus the last 5 turns in each request.  
- ✅ Assistant keeps recent + summarized older context while staying within token limits.  

---

## 3. Customer Service Bot (Tool Calling)

Extend the chatbot with **three tools** that simulate retail customer support tasks:  

1. **Get Order Status**  
   - Input: `order_id`  
   - Output: *“Order ORD123 is Out for Delivery.”*  

2. **Price Lookup**  
   - Input: `product_name`  
   - Output: *“Current price for Samsung TV is $499.”*  

3. **Store Locator**  
   - Input: `zip_code`  
   - Output: *“Store in ZIP 10001 is Walmart Supercenter.”*  

✅ Assistant calls the right tool mid-conversation and integrates the tool’s results naturally in its reply.  

**Optional Extensions (for fast learners):**  
- **Delivery Estimate** → *“Expected delivery in 3 days.”*  
- **Store Hours Finder** → *“Store in ZIP 10001 closes at 11 PM.”*  
- **Online Product Availability** → *“iPhone 15 is available online and ready to ship.”*  

---

## 4. Guardrails & Filters (Responsible AI)

Add **input/output filters** before showing responses. Cover three categories:  

- **PII Redaction** → remove phone numbers, emails, credit card-like patterns before sending to model.  
- **Abusive Language** → detect toxic/abusive inputs and respond politely: *“I cannot respond to offensive content.”*  

✅ Assistant handles unsafe/abusive/PII cases gracefully without leaking sensitive info.  

---

## 5. Make Your Own Bot 🎨

- Create a bot with its own **system prompt** and at least one special feature (multi-modal/tool etc).  
- Examples: *Product guru*, *FAQ generator*, *Ad copy bot*.  
- ✅ Must show a clear difference from the base chatbot.  

---

Happy coding! 🚀
