#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF to TXT Converter Application
Main entry point for the application
"""

import os
import sys
import logging
from pdf_converter import PDFConverter

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function to run the PDF to TXT converter application"""
    try:
        # Default directories (using relative paths for Replit environment)
        source_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "TaiVe")
        target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "TaiVe_Done")
        
        # Check if source directory exists
        if not os.path.exists(source_dir):
            logger.error(f"Thư mục nguồn '{source_dir}' không tồn tại.")
            return
        
        # Create target directory if it doesn't exist
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            logger.info(f"Đã tạo thư mục đích '{target_dir}'")
        
        # Initialize converter
        converter = PDFConverter(source_dir, target_dir)
        
        # Start conversion process
        converter.process_all_pdfs()
        
        # Display completion message
        logger.info("Hoàn tất")
        
    except Exception as e:
        logger.error(f"Lỗi không xác định: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
