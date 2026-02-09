import pymupdf 
from fastapi import UploadFile, HTTPException

async def extract_text_from_pdf(file: UploadFile) -> str:
    """
    Extracts text from an uploaded PDF file using PyMuPDF.
    """
    try:
        # Read the file bytes into memory
        file_content = await file.read()
        
        # Open the document from memory (stream)
        # We specify filetype="pdf" to tell pymupdf it's a PDF stream
        with pymupdf.open(stream=file_content, filetype="pdf") as doc:
            full_text = ""
            for page in doc: # iterate the document pages
                full_text += page.get_text() + "\n" # type: ignore # get plain text encoded as UTF-8
                
        return full_text # type: ignore

    except Exception as e:
        print(f"Error parsing PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse PDF file.")