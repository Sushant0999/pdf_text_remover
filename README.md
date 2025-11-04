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

