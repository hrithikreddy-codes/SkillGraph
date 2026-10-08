import io
import pypdf
import docx

def extract_text(uploaded_file):
    """
    Extracts text from a Streamlit UploadedFile based on its extension.
    Supports .pdf, .docx, and .txt formats.
    """
    if not uploaded_file:
        return ""
        
    filename = uploaded_file.name.lower()
    text = ""
    
    try:
        # Streamlit UploadedFile behaves like a file object
        if filename.endswith(".pdf"):
            uploaded_file.seek(0)
            reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    
        elif filename.endswith(".docx"):
            uploaded_file.seek(0)
            doc = docx.Document(io.BytesIO(uploaded_file.read()))
            for para in doc.paragraphs:
                if para.text:
                    text += para.text + "\n"
                    
        elif filename.endswith(".txt"):
            uploaded_file.seek(0)
            text = uploaded_file.read().decode("utf-8", errors="ignore")
            
    except Exception:
        return ""
        
    result = text.strip()
    return result if result else ""
