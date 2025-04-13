#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF Converter Module
Handles conversion of PDF files to TXT with UTF-8 encoding
"""

import os
import shutil
import logging
import pdfplumber

logger = logging.getLogger(__name__)

class PDFConverter:
    """Class to handle PDF to TXT conversion and file organization"""
    
    def __init__(self, source_dir, target_dir):
        """
        Initialize the converter with source and target directories
        
        Args:
            source_dir (str): Directory containing PDF files to convert
            target_dir (str): Directory to move processed PDF files
        """
        self.source_dir = source_dir
        self.target_dir = target_dir
        
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text from PDF file with proper UTF-8 encoding
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text content with UTF-8 encoding
        """
        text_content = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    text_content += text + "\n\n"
            return text_content
        except Exception as e:
            logger.error(f"Lỗi khi trích xuất văn bản từ PDF: {e}")
            raise
    
    def save_text_to_file(self, text_content, output_path):
        """
        Save extracted text to a file with UTF-8 encoding
        
        Args:
            text_content (str): Text content to save
            output_path (str): Path where the TXT file will be saved
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(text_content)
        except Exception as e:
            logger.error(f"Lỗi khi lưu file TXT: {e}")
            raise
    
    def move_processed_file(self, source_path, target_dir):
        """
        Move processed PDF file to target directory
        
        Args:
            source_path (str): Path of the PDF file to move
            target_dir (str): Target directory to move the file to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            filename = os.path.basename(source_path)
            target_path = os.path.join(target_dir, filename)
            
            # If target file already exists, create a unique name
            if os.path.exists(target_path):
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(target_path):
                    new_filename = f"{base}_{counter}{ext}"
                    target_path = os.path.join(target_dir, new_filename)
                    counter += 1
            
            shutil.move(source_path, target_path)
            logger.info(f"Đã di chuyển {filename}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi di chuyển file: {e}")
            return False
    
    def convert_pdf_to_txt(self, pdf_path):
        """
        Convert a PDF file to TXT with UTF-8 encoding
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            bool: True if conversion successful, False otherwise
        """
        filename = os.path.basename(pdf_path)
        logger.info(f"Đang convert {filename}")
        
        try:
            # Extract text from PDF
            text_content = self.extract_text_from_pdf(pdf_path)
            
            # Create output path with .txt extension
            output_filename = os.path.splitext(filename)[0] + '.txt'
            output_path = os.path.join(self.source_dir, output_filename)
            
            # Save text to file with UTF-8 encoding
            self.save_text_to_file(text_content, output_path)
            
            logger.info(f"Convert thành công {filename}")
            return True
        except Exception as e:
            logger.error(f"Convert Fail {filename}: {e}")
            return False
    
    def process_all_pdfs(self):
        """
        Process all PDF files in the source directory
        Convert them to TXT and move them to target directory
        """
        pdf_files = [f for f in os.listdir(self.source_dir) 
                    if f.lower().endswith('.pdf') and 
                    os.path.isfile(os.path.join(self.source_dir, f))]
        
        if not pdf_files:
            logger.info(f"Không tìm thấy file PDF nào trong {self.source_dir}")
            return
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.source_dir, pdf_file)
            
            # Convert PDF to TXT
            success = self.convert_pdf_to_txt(pdf_path)
            
            # If conversion was successful, move the PDF file
            if success:
                self.move_processed_file(pdf_path, self.target_dir)
