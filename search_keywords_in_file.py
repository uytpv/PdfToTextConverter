import os
import logging
from app import app, db
from models import Keyword, KeywordMatch, ProcessedFile
from keyword_extractor import KeywordExtractor

# Thiết lập logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def search_keywords_in_file(txt_filename):
    """
    Tìm kiếm từ khóa trong một file TXT cụ thể
    
    Args:
        txt_filename (str): Tên file TXT cần tìm kiếm
    """
    source_dir = "TaiVe"
    txt_path = os.path.join(source_dir, txt_filename)
    
    if not os.path.exists(txt_path):
        logger.error(f"File không tồn tại: {txt_path}")
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
            processed_file = ProcessedFile.query.filter_by(file_name=txt_filename).first()
            if not processed_file:
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
                
                # Kiểm tra xem đã có kết quả cho từ khóa này chưa
                existing_matches = KeywordMatch.query.filter_by(
                    keyword_id=keyword.id,
                    file_name=txt_filename
                ).count()
                
                if existing_matches > 0:
                    logger.info(f"Đã có {existing_matches} kết quả cho từ khóa '{keyword_text}' trong file {txt_filename}")
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

if __name__ == "__main__":
    # Tên file TXT cần tìm kiếm
    txt_filename = "1634019886t3d03js864o5.txt"
    search_keywords_in_file(txt_filename)