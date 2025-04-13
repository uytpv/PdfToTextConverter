import os
import logging
from pdf_converter import PDFConverter

def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger(__name__)
    
    # Define source and destination directories using relative paths
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(current_dir, "TaiVe")
    dest_dir = os.path.join(current_dir, "TaiVe_Done")
    
    # Create destination directory if it doesn't exist
    if not os.path.exists(dest_dir):
        try:
            os.makedirs(dest_dir)
            logger.info(f"Created destination directory: {dest_dir}")
        except OSError as e:
            logger.error(f"Error creating destination directory: {e}")
            return
    
    # Initialize converter
    converter = PDFConverter(source_dir, dest_dir)
    
    # Process all PDF files
    converter.process_all_pdfs()
    
    logger.info("Hoàn tất")

if __name__ == "__main__":
    main()
