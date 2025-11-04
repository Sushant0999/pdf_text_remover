# 🧹 PDF Answer Cleaner (OCR Based)

This tool automatically **removes answers from question PDFs**, including scanned documents.  
Useful for students, teachers, institutes, and self-practice revision.

### ✨ Features
- ✅ Detects and removes **Ans. (c), Ans: b, Answer: d** etc.
- ✅ Removes **Explanation / Solution** headers cleanly
- ✅ Works with **scanned PDFs** (OCR based)
- ✅ Keeps the **original text searchable**
- ✅ Easy UI made with **Streamlit**
- ✅ No ML training required

---

### 🔧 How It Works
1. PDF page is converted to an image.
2. OCR (Tesseract) extracts text with bounding boxes.
3. Answer keywords and option text are located.
4. Those bounding boxes are **redacted** (removed).
5. Clean PDF is generated.

---

### 🖥️ Run Locally

pip install -r requirements.txt
streamlit run app.py


docker build -t pdf-cleaner .
docker run -p 8501:8501 pdf-cleaner


Then open: http://localhost:8501

---

### 📦 Requirements
| Library | Purpose |
|--------|---------|
| **pytesseract** | OCR text extraction |
| **pdf2image** | Convert PDF → Image |
| **pymupdf (fitz)** | Apply redaction |
| **Streamlit** | User Interface |

Ensure **Tesseract** and **Poppler** are installed on your OS.

---

### 💙 Author
Sushant  
(Feel free to star ⭐ the repo if you find it useful)


