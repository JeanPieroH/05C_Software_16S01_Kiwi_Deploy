import PyPDF2
import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class PDFExtractor:
    """
    Clase para extraer texto de archivos PDF
    """
    
    @staticmethod
    async def extract_text_from_pdf(file_content: bytes) -> str:
        """
        Extrae el texto de un archivo PDF proporcionado como bytes
        
        Args:
            file_content: Contenido del archivo PDF en bytes
            
        Returns:
            Texto extraído del PDF
        """
        try:
            # Crear un objeto de lectura de PDF a partir de los bytes
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extraer texto de cada página
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n\n"
                
            return text
        except Exception as e:
            logger.error(f"Error extrayendo texto del PDF: {str(e)}")
            raise
