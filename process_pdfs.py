import os
import logging
from pdf_converter import PDFConverter
from keyword_extractor import KeywordExtractor
from database_manager import DatabaseManager

# Thiết lập logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Chức năng chính để xử lý các file PDF và tìm kiếm từ khóa
    """
    # Khởi tạo thư mục
    source_dir = "TaiVe"
    dest_dir = "TaiVe_Done"
    
    # Đảm bảo thư mục đích tồn tại
    os.makedirs(dest_dir, exist_ok=True)
    
    # Khởi tạo PDF Converter
    logger.info("Bắt đầu chuyển đổi PDF")
    converter = PDFConverter(source_dir, dest_dir)
    
    # Xử lý tất cả các file PDF trong thư mục nguồn
    converter.process_all_pdfs()
    
    # Sau khi chuyển đổi, tìm kiếm từ khóa trong các file TXT
    logger.info("Bắt đầu tìm kiếm từ khóa")
    
    # Khởi tạo Database Manager để lấy từ khóa
    db_manager = DatabaseManager()
    
    # Lấy tất cả từ khóa từ cơ sở dữ liệu
    keywords = db_manager.get_keywords_as_list()
    
    if not keywords:
        logger.warning("Không có từ khóa trong cơ sở dữ liệu")
        return
    
    logger.info(f"Tìm thấy {len(keywords)} từ khóa trong cơ sở dữ liệu")
    
    # Khởi tạo Keyword Extractor
    extractor = KeywordExtractor(keywords)
    
    # Tìm tất cả file TXT trong thư mục nguồn
    txt_files = [f for f in os.listdir(source_dir) 
               if f.lower().endswith('.txt') and 
               os.path.isfile(os.path.join(source_dir, f))]
    
    if not txt_files:
        logger.warning("Không có file TXT để tìm kiếm từ khóa")
        return
    
    logger.info(f"Tìm thấy {len(txt_files)} file TXT để tìm kiếm")
    
    # Xử lý từng file TXT
    for txt_file in txt_files:
        txt_path = os.path.join(source_dir, txt_file)
        logger.info(f"Đang tìm kiếm từ khóa trong {txt_file}")
        
        try:
            # Tìm kiếm từ khóa trong file
            keyword_matches = extractor.extract_from_file(txt_path)
            
            if not keyword_matches:
                logger.info(f"Không tìm thấy từ khóa nào trong {txt_file}")
                continue
            
            # Lưu kết quả tìm kiếm vào cơ sở dữ liệu
            matches_count = sum(len(matches) for matches in keyword_matches.values())
            logger.info(f"Tìm thấy {matches_count} kết quả cho {len(keyword_matches)} từ khóa trong {txt_file}")
            
            # Lưu kết quả tìm kiếm và đánh dấu file đã xử lý
            db_manager.save_keyword_matches(txt_file, keyword_matches)
            db_manager.mark_file_as_processed(txt_file, txt_path)
            
            logger.info(f"Đã lưu kết quả tìm kiếm cho {txt_file}")
        except Exception as e:
            logger.error(f"Lỗi khi xử lý file {txt_file}: {e}")
    
    logger.info("Quá trình tìm kiếm từ khóa đã hoàn tất")
    
if __name__ == "__main__":
    main()