# import streamlit as st
# import re
# import fitz
# from pdf2image import convert_from_path
# import pytesseract
# from pytesseract import Output
# from pathlib import Path

# # -------- CONFIG --------
# POPPLER_PATH = None  # if poppler is installed in PATH leave None

# # -------- PATTERNS --------
# ANS_PATTERN = re.compile(r"(?i)^ans[:.\s]*$")
# LETTER_PATTERN = re.compile(r"(?i)^\(?[a-d]\)?$")

# OTHER_PATTERNS = [
#     re.compile(r"(?i)^answer[:.]?$"),
#     re.compile(r"(?i)^solution[:.]?$"),
#     re.compile(r"(?i)^explanation[:.]?$"),
# ]


# def find_ans_sequences(words):
#     boxes = []
#     n = len(words)

#     for i, w in enumerate(words):
#         text = (w["text"] or "").strip()
#         if not text:
#             continue

#         # 1️⃣ CASE: "Ans" + letter next word
#         if ANS_PATTERN.match(text):
#             coords = [w["left"], w["top"], w["left"] + w["width"], w["top"] + w["height"]]
#             for j in range(1, 4):
#                 if i + j >= n:
#                     break
#                 nxt = (words[i + j]["text"] or "").strip()
#                 if not nxt:
#                     continue

#                 coords[2] = max(coords[2], words[i + j]["left"] + words[i + j]["width"])
#                 coords[3] = max(coords[3], words[i + j]["top"] + words[i + j]["height"])
#                 coords[0] = min(coords[0], words[i + j]["left"])
#                 coords[1] = min(coords[1], words[i + j]["top"])

#                 if LETTER_PATTERN.match(nxt):
#                     boxes.append(tuple(coords))
#                     break
#             continue

#         # 2️⃣ CASE: "Ans.(c)" in same token
#         if ANS_PATTERN.search(text) and LETTER_PATTERN.search(text):
#             left = w["left"]
#             top = w["top"]
#             right = w["left"] + w["width"]
#             bottom = w["top"] + w["height"]
#             boxes.append((left, top, right, bottom))
#             continue

#         # 3️⃣ CASE: Remove explanation lines
#         for pat in OTHER_PATTERNS:
#             if pat.search(text):
#                 band_top = w["top"] - 3
#                 band_bottom = w["top"] + w["height"] + 3

#                 xs, xrs = [], []
#                 for k in range(n):
#                     if not words[k]["text"].strip():
#                         continue
#                     # keep same line only
#                     if not (words[k]["top"] > band_bottom or (words[k]["top"] + words[k]["height"]) < band_top):
#                         xs.append(words[k]["left"])
#                         xrs.append(words[k]["left"] + words[k]["width"])

#                 if xs and xrs:
#                     boxes.append((min(xs), band_top, max(xrs), band_bottom))
#                 break

#     return boxes


# def image_to_pdf_rect(b, img_size, rect):
#     img_w, img_h = img_size
#     pdf_w, pdf_h = rect.width, rect.height
#     x_scale = pdf_w / img_w
#     y_scale = pdf_h / img_h
#     l, t, r, bt = b
#     return fitz.Rect(l * x_scale, t * y_scale, r * x_scale, bt * y_scale)


# # ---------- STREAMLIT UI ----------
# st.title("🧹 PDF Answer Cleaner (OCR Based)")

# uploaded = st.file_uploader("Upload PDF", type=["pdf"])
# dpi = st.slider("OCR DPI (Recommended: 300)", 150, 500, 300)

# if uploaded:
#     temp_pdf = "uploaded.pdf"
#     with open(temp_pdf, "wb") as f:
#         f.write(uploaded.read())

#     if st.button("Start Cleaning"):
#         pdf_out = fitz.open(temp_pdf)
#         total_pages = pdf_out.page_count

#         progress = st.progress(0)
#         status = st.empty()

#         for i in range(total_pages):
#             status.text(f"Processing Page {i+1}/{total_pages}")

#             image = convert_from_path(
#                 temp_pdf, dpi=dpi, first_page=i+1, last_page=i+1, poppler_path=POPPLER_PATH
#             )[0]
#             page = pdf_out[i]

#             data = pytesseract.image_to_data(image, output_type=Output.DICT, config="--psm 6")
#             words = [
#                 {"text": t, "left": l, "top": tp, "width": w, "height": h}
#                 for t, l, tp, w, h in zip(data["text"], data["left"], data["top"], data["width"], data["height"])
#             ]

#             boxes = find_ans_sequences(words)

#             for b in boxes:
#                 rect = image_to_pdf_rect(b, image.size, page.rect)
#                 page.add_redact_annot(rect, fill=(1, 1, 1))

#             if boxes:
#                 page.apply_redactions()

#             progress.progress((i + 1) / total_pages)

#         output_file = Path(uploaded.name).stem + "_cleaned.pdf"
#         pdf_out.save(output_file)

#         st.success("✅ Done! Cleaning complete.")
#         st.download_button("⬇️ Download Clean PDF", open(output_file, "rb"), file_name=output_file)



import streamlit as st
import re
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
from pytesseract import Output
from pathlib import Path
import os

# -------- CONFIG --------
POPPLER_PATH = None  # Set this if poppler is not in PATH

# -------- DEFAULT PATTERNS --------
DEFAULT_PATTERNS = [
    r"(?i)^ans[:.\s]*$",
    r"(?i)^\(?[a-d]\)?$",
    r"(?i)^answer[:.]?$",
    r"(?i)^solution[:.]?$",
    r"(?i)^explanation[:.]?$"
]


def compile_patterns(user_text):
    """Combine default patterns with user input patterns."""
    patterns = [re.compile(p) for p in DEFAULT_PATTERNS]
    if user_text:
        custom_texts = [t.strip() for t in user_text.split(",") if t.strip()]
        for t in custom_texts:
            patterns.append(re.compile(re.escape(t), re.IGNORECASE))
    return patterns


def find_ans_sequences(words, patterns):
    boxes = []
    n = len(words)

    for i, w in enumerate(words):
        text = (w["text"] or "").strip()
        if not text:
            continue

        for pat in patterns:
            if pat.search(text):
                left, top = w["left"], w["top"]
                right, bottom = left + w["width"], top + w["height"]
                boxes.append((left, top, right, bottom))
                break

    return boxes


def image_to_pdf_rect(b, img_size, rect):
    img_w, img_h = img_size
    pdf_w, pdf_h = rect.width, rect.height
    x_scale = pdf_w / img_w
    y_scale = pdf_h / img_h
    l, t, r, bt = b
    return fitz.Rect(l * x_scale, t * y_scale, r * x_scale, bt * y_scale)


# -------- STREAMLIT APP --------
st.title("🧹 PDF Text Cleaner (OCR Based)")
st.caption("Removes selected text (like 'Ans', 'Solution', or any custom words) from PDFs using OCR")

uploaded_file = st.file_uploader("📄 Upload a PDF", type=["pdf"])
user_input = st.text_input(
    "🔍 Enter words to remove (comma-separated):",
    placeholder="e.g., Ans, Solution, Explanation, Answer"
)
dpi = st.slider("OCR DPI (Higher = More Accurate, Slower)", 150, 500, 300)

if uploaded_file:
    temp_pdf = "uploaded.pdf"
    total_size = uploaded_file.size
    bytes_written = 0

    progress = st.progress(0)
    st.write("Uploading file...")

    with open(temp_pdf, "wb") as f:
        while True:
            chunk = uploaded_file.read(1024 * 1024)  # 1MB chunks
            if not chunk:
                break
            f.write(chunk)
            bytes_written += len(chunk)
            progress.progress(min(bytes_written / total_size, 1.0))

    st.success("✅ Upload complete!")

    if st.button("🚀 Start Cleaning"):
        pdf_out = fitz.open(temp_pdf)
        total_pages = pdf_out.page_count
        clean_progress = st.progress(0)
        status = st.empty()

        compiled_patterns = compile_patterns(user_input)

        for i in range(total_pages):
            status.text(f"Processing Page {i + 1}/{total_pages}")
            image = convert_from_path(temp_pdf, dpi=dpi, first_page=i + 1, last_page=i + 1, poppler_path=POPPLER_PATH)[0]
            page = pdf_out[i]

            data = pytesseract.image_to_data(image, output_type=Output.DICT, config="--psm 6")
            words = [
                {"text": t, "left": l, "top": tp, "width": w, "height": h}
                for t, l, tp, w, h in zip(data["text"], data["left"], data["top"], data["width"], data["height"])
            ]

            boxes = find_ans_sequences(words, compiled_patterns)
            for b in boxes:
                rect = image_to_pdf_rect(b, image.size, page.rect)
                page.add_redact_annot(rect, fill=(1, 1, 1))

            if boxes:
                page.apply_redactions()

            clean_progress.progress((i + 1) / total_pages)

        output_file = Path(uploaded_file.name).stem + "_cleaned.pdf"
        pdf_out.save(output_file)

        st.success("✅ Cleaning complete!")
        st.download_button("⬇️ Download Clean PDF", open(output_file, "rb"), file_name=output_file)
