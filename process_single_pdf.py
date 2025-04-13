import os
import logging
from app import app, db
from models import Keyword, KeywordMatch, ProcessedFile
from pdf_converter import PDFConverter
from keyword_extractor import KeywordExtractor
from database_manager import DatabaseManager

# Thiết lập logging
logging.basicConfig(level=logging.INFO,
                  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_single_pdf(pdf_filename):
    """
    Xử lý một file PDF cụ thể và tìm kiếm từ khóa
    
    Args:
        pdf_filename (str): Tên file PDF cần xử lý (đã có trong thư mục TaiVe)
    """
    # Khởi tạo thư mục
    source_dir = "TaiVe"
    dest_dir = "TaiVe_Done"
    
    # Đảm bảo thư mục đích tồn tại
    os.makedirs(dest_dir, exist_ok=True)
    
    # Đường dẫn đầy đủ đến file PDF
    pdf_path = os.path.join(source_dir, pdf_filename)
    
    if not os.path.exists(pdf_path):
        logger.error(f"File không tồn tại: {pdf_path}")
        return
    
    # Khởi tạo PDF Converter
    logger.info(f"Bắt đầu chuyển đổi PDF: {pdf_filename}")
    converter = PDFConverter(source_dir, dest_dir)
    
    # Chuyển đổi PDF thành TXT
    if converter.convert_pdf_to_txt(pdf_path):
        logger.info(f"Chuyển đổi thành công: {pdf_filename}")
        
        # Di chuyển file PDF sau khi chuyển đổi thành công
        converter.move_pdf_file(pdf_path)
        
        # Tên file TXT
        txt_filename = os.path.splitext(pdf_filename)[0] + ".txt"
        txt_path = os.path.join(source_dir, txt_filename)
        
        # Kiểm tra xem file TXT đã được tạo chưa
        if not os.path.exists(txt_path):
            logger.error(f"File TXT không tồn tại sau khi chuyển đổi: {txt_path}")
            return
        
        logger.info(f"Bắt đầu tìm kiếm từ khóa trong file: {txt_filename}")
        
        # Sử dụng app context cho các thao tác với cơ sở dữ liệu
        with app.app_context():
            # Lấy tất cả từ khóa từ cơ sở dữ liệu
            keywords = Keyword.query.all()
            keyword_list = [k.keyword for k in keywords]
            
            if not keyword_list:
                logger.warning("Không có từ khóa trong cơ sở dữ liệu")
                return
            
            logger.info(f"Tìm thấy {len(keyword_list)} từ khóa trong cơ sở dữ liệu")
            
            # Khởi tạo Keyword Extractor
            extractor = KeywordExtractor(keyword_list)
            
            try:
                # Tìm kiếm từ khóa trong file
                keyword_matches = extractor.extract_from_file(txt_path)
                
                if not keyword_matches:
                    logger.info(f"Không tìm thấy từ khóa nào trong {txt_filename}")
                    return
                
                # Lưu kết quả tìm kiếm vào cơ sở dữ liệu
                matches_count = sum(len(matches) for matches in keyword_matches.values())
                logger.info(f"Tìm thấy {matches_count} kết quả cho {len(keyword_matches)} từ khóa trong {txt_filename}")
                
                # Tạo bản ghi file đã xử lý
                processed_file = ProcessedFile(
                    file_name=txt_filename,
                    file_path=txt_path,
                    status='processed'
                )
                db.session.add(processed_file)
                db.session.commit()
                
                # Lưu các kết quả từ khóa
                for keyword_text, matches in keyword_matches.items():
                    # Tìm từ khóa trong cơ sở dữ liệu
                    keyword = Keyword.query.filter_by(keyword=keyword_text).first()
                    if not keyword:
                        logger.warning(f"Không tìm thấy từ khóa trong cơ sở dữ liệu: {keyword_text}")
                        continue
                    
                    # Lưu từng kết quả
                    for match_content in matches:
                        keyword_match = KeywordMatch(
                            keyword_id=keyword.id,
                            file_name=txt_filename,
                            content=match_content
                        )
                        db.session.add(keyword_match)
                
                db.session.commit()
                logger.info(f"Đã lưu kết quả tìm kiếm cho {txt_filename}")
                
            except Exception as e:
                db.session.rollback()
                logger.error(f"Lỗi khi xử lý file {txt_filename}: {e}")
    else:
        logger.error(f"Chuyển đổi thất bại: {pdf_filename}")

if __name__ == "__main__":
    # Tên file PDF cần xử lý
    pdf_filename = "1634019886t3d03js864o5.pdf"
    process_single_pdf(pdf_filename)