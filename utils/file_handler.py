import PyPDF2
import docx
from typing import Union
import io

class FileHandler:
    """Handle file uploads and text extraction."""
    
    @staticmethod
    def extract_text(file) -> str:
        """Extract text from uploaded file (PDF, TXT, DOCX)."""
        file_type = file.name.split('.')[-1].lower()
        
        try:
            if file_type == 'pdf':
                return FileHandler._extract_from_pdf(file)
            elif file_type == 'txt':
                return file.read().decode('utf-8')
            elif file_type == 'docx':
                return FileHandler._extract_from_docx(file)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            raise Exception(f"Error extracting text: {str(e)}")
    
    @staticmethod
    def _extract_from_pdf(file) -> str:
        """Extract text from PDF file."""
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    
    @staticmethod
    def _extract_from_docx(file) -> str:
        """Extract text from DOCX file."""
        doc = docx.Document(io.BytesIO(file.read()))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text