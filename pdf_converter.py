import os
import shutil
import logging
import PyPDF2
import pdfplumber
from pathlib import Path

class PDFConverter:
    def __init__(self, source_dir, dest_dir):
        """
        Initialize the PDF Converter
        
        Args:
            source_dir (str): Directory containing PDF files to convert
            dest_dir (str): Directory to move processed PDF files
        """
        self.source_dir = source_dir
        self.dest_dir = dest_dir
        self.logger = logging.getLogger(__name__)
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text from a PDF file
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text with UTF-8 encoding
        """
        try:
            # Try pdfplumber for better Unicode support
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                
                if text.strip():
                    return text
                    
            # Fallback to PyPDF2 if pdfplumber didn't extract any text
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                
                # Ensure text is properly encoded for Vietnamese
                return text
        except Exception as e:
            self.logger.error(f"Error extracting text from {pdf_path}: {e}")
            return None
    
    def convert_pdf_to_txt(self, pdf_path):
        """
        Convert a PDF file to TXT
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            bool: True if conversion was successful, False otherwise
        """
        filename = os.path.basename(pdf_path)
        self.logger.info(f"Đang convert {filename}")
        
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_path)
        
        if text is None:
            self.logger.info(f"Convert thất bại {filename}")
            return False
        
        # Create txt file with the same name
        txt_filename = os.path.splitext(filename)[0] + ".txt"
        txt_path = os.path.join(os.path.dirname(pdf_path), txt_filename)
        
        try:
            # Write text to file with UTF-8 encoding
            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text)
            self.logger.info(f"Convert thành công {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Error writing to {txt_path}: {e}")
            self.logger.info(f"Convert thất bại {filename}")
            return False
    
    def move_pdf_file(self, pdf_path):
        """
        Move a PDF file to the destination directory
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            bool: True if moving was successful, False otherwise
        """
        filename = os.path.basename(pdf_path)
        dest_path = os.path.join(self.dest_dir, filename)
        
        try:
            shutil.move(pdf_path, dest_path)
            self.logger.info(f"Đã di chuyển {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Error moving {pdf_path} to {dest_path}: {e}")
            return False
    
    def process_all_pdfs(self):
        """
        Process all PDF files in the source directory
        """
        # Get all PDF files
        try:
            pdf_files = [f for f in os.listdir(self.source_dir) 
                        if f.lower().endswith('.pdf') and 
                        os.path.isfile(os.path.join(self.source_dir, f))]
        except Exception as e:
            self.logger.error(f"Error accessing source directory: {e}")
            return
        
        if not pdf_files:
            self.logger.info(f"No PDF files found in {self.source_dir}")
            return
        
        # Process each PDF file
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.source_dir, pdf_file)
            
            # Convert PDF to TXT
            if self.convert_pdf_to_txt(pdf_path):
                # Move the PDF file if conversion was successful
                self.move_pdf_file(pdf_path)
