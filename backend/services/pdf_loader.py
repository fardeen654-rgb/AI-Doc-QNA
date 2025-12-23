import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file using PyMuPDF.
    """
    text = ""

    try:
        # Open the PDF document
        doc = fitz.open(pdf_path)

        # Iterate through each page and extract text
        for page_num in range(len(doc)):
            page = doc[page_num]
            text += page.get_text()

        doc.close()

    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

    # Return trimmed text to remove leading/trailing whitespace
    return text.strip()