import streamlit as st
from pypdf import PdfReader, PdfWriter
from PIL import Image
from io import BytesIO
import re

st.set_page_config(
    page_title="PDF Master",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.stApp {background: linear-gradient(180deg, #f5f7ff 0%, #ffffff 45%);}
.block-container {max-width: 850px; padding-top: 1.5rem; padding-bottom: 2rem;}
.hero {padding: 24px; border-radius: 22px; background: linear-gradient(135deg,#243b8a,#6c42c7); color: white; margin-bottom: 18px;}
.hero h1 {color:white; margin:0; font-size:2rem;}
.hero p {color:#e9e9ff; margin:8px 0 0 0;}
div.stButton > button {border-radius: 12px; min-height: 44px;}
div[data-testid="stFileUploader"] {background:#ffffff; border-radius:14px;}
.small-note {font-size: 0.88rem; color:#5e6475;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>📄 PDF Master</h1>
  <p>Your simple PDF toolkit — merge, split, convert images, and extract text.</p>
</div>
""", unsafe_allow_html=True)

st.info("Free starter version. Files are processed by this app server while you use it. Do not upload highly sensitive documents to a public demo.")

tool = st.radio(
    "Choose a tool",
    ["Merge PDF", "Split PDF", "Images to PDF", "PDF to Text"],
    horizontal=False
)

def valid_pdf(upload):
    try:
        reader = PdfReader(BytesIO(upload.getvalue()))
        if reader.is_encrypted:
            st.error(f"{upload.name}: password-protected PDFs are not supported in this version.")
            return None
        return reader
    except Exception:
        st.error(f"{upload.name} could not be read as a PDF. Please choose a valid, uncorrupted PDF.")
        return None

def parse_pages(spec, total):
    """Convert page input like 1-3,5 into zero-based page indexes."""
    indexes = []
    parts = [p.strip() for p in spec.split(",") if p.strip()]
    if not parts:
        raise ValueError("Enter page numbers, for example 1-3,5.")
    for part in parts:
        if re.fullmatch(r"\d+", part):
            start = end = int(part)
        elif re.fullmatch(r"\d+\s*-\s*\d+", part):
            a, b = [int(x.strip()) for x in part.split("-")]
            if a > b:
                raise ValueError(f"Invalid range: {part}. Start page must be less than or equal to end page.")
            start, end = a, b
        else:
            raise ValueError(f"Invalid page entry: {part}. Use formats like 1-3,5.")
        if start < 1 or end > total:
            raise ValueError(f"Pages must be between 1 and {total}.")
        indexes.extend(range(start - 1, end))
    # Preserve requested order but avoid duplicate pages.
    return list(dict.fromkeys(indexes))

if tool == "Merge PDF":
    st.subheader("Combine multiple PDF files")
    files = st.file_uploader("Choose 2 or more PDF files", type=["pdf"], accept_multiple_files=True)
    if files:
        st.caption(f"{len(files)} file(s) selected. Files will be merged in the order shown below.")
        for i, f in enumerate(files, 1):
            st.write(f"{i}. {f.name}")
    if st.button("Merge PDFs", type="primary", use_container_width=True):
        if not files or len(files) < 2:
            st.warning("Please select at least two PDF files.")
        else:
            writer = PdfWriter()
            try:
                for f in files:
                    reader = valid_pdf(f)
                    if reader is None:
                        st.stop()
                    for page in reader.pages:
                        writer.add_page(page)
                output = BytesIO()
                writer.write(output)
                st.success("PDFs merged successfully.")
                st.download_button("⬇️ Download merged PDF", output.getvalue(),
                                   file_name="merged_pdf_master.pdf",
                                   mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.error(f"Could not merge these files: {e}")

elif tool == "Split PDF":
    st.subheader("Extract selected pages")
    file = st.file_uploader("Upload one PDF", type=["pdf"], key="split_pdf")
    if file:
        reader = valid_pdf(file)
        if reader:
            st.write(f"**File:** {file.name} · **Pages:** {len(reader.pages)}")
            spec = st.text_input("Pages to extract", placeholder="Example: 1-3,5")
            st.caption("Page numbers start at 1. Example 1-3,5 extracts pages 1, 2, 3 and 5.")
            if st.button("Create new PDF", type="primary", use_container_width=True):
                try:
                    indexes = parse_pages(spec, len(reader.pages))
                    writer = PdfWriter()
                    for idx in indexes:
                        writer.add_page(reader.pages[idx])
                    output = BytesIO()
                    writer.write(output)
                    st.success(f"Created a PDF with {len(indexes)} page(s).")
                    st.download_button("⬇️ Download extracted PDF", output.getvalue(),
                                       file_name="extracted_pages.pdf",
                                       mime="application/pdf", use_container_width=True)
                except ValueError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Could not split this PDF: {e}")

elif tool == "Images to PDF":
    st.subheader("Turn photos into one PDF")
    files = st.file_uploader("Choose images (JPG, JPEG, or PNG)", type=["jpg", "jpeg", "png"],
                             accept_multiple_files=True, key="images")
    if files:
        st.caption(f"{len(files)} image(s) selected. The order below is the PDF page order.")
        for i, f in enumerate(files, 1):
            st.write(f"{i}. {f.name}")
    if st.button("Convert images to PDF", type="primary", use_container_width=True):
        if not files:
            st.warning("Please select at least one image.")
        else:
            try:
                pages = []
                for f in files:
                    img = Image.open(BytesIO(f.getvalue()))
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    pages.append(img.copy())
                output = BytesIO()
                pages[0].save(output, format="PDF", save_all=True, append_images=pages[1:])
                st.success(f"Converted {len(pages)} image(s) into a PDF.")
                st.download_button("⬇️ Download images PDF", output.getvalue(),
                                   file_name="images_to_pdf.pdf",
                                   mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.error(f"Could not convert these images: {e}")

elif tool == "PDF to Text":
    st.subheader("Extract selectable text from a PDF")
    file = st.file_uploader("Upload one PDF", type=["pdf"], key="text_pdf")
    if file:
        if st.button("Extract text", type="primary", use_container_width=True):
            reader = valid_pdf(file)
            if reader:
                try:
                    chunks = []
                    for i, page in enumerate(reader.pages, 1):
                        chunks.append(f"--- Page {i} ---\n{page.extract_text() or '[No selectable text found on this page]'}")
                    text = "\n\n".join(chunks)
                    st.text_area("Extracted text", value=text, height=320)
                    st.download_button("⬇️ Download text file", text.encode("utf-8"),
                                       file_name="extracted_text.txt",
                                       mime="text/plain", use_container_width=True)
                    st.caption("Scanned/photo PDFs may need OCR; OCR is not included in this starter version.")
                except Exception as e:
                    st.error(f"Could not extract text: {e}")

st.divider()
st.markdown("**PDF Master · Version 1.0**")
st.markdown('<p class="small-note">Made for simple everyday PDF tasks. Always keep your original files as a backup.</p>', unsafe_allow_html=True)
