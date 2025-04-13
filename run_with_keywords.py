import os
import sys
import logging
from pdf_converter import PDFConverter
from keyword_extractor import KeywordExtractor
from models import Keyword
from app import app, db

# Thiết lập logging
logging.basicConfig(level=logging.INFO,
                  format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_pdf_with_keywords(keywords_list=None):
    """
    Xử lý tất cả các file PDF, tìm kiếm từ khóa và lưu trữ kết quả
    
    Args:
        keywords_list (list, optional): Danh sách từ khóa cần tìm. Nếu None, sẽ sử dụng từ cơ sở dữ liệu.
    """
    # Khởi tạo thư mục
    source_dir = "TaiVe"
    dest_dir = "TaiVe_Done"
    
    # Đảm bảo thư mục tồn tại
    os.makedirs(source_dir, exist_ok=True)
    os.makedirs(dest_dir, exist_ok=True)
    
    # Khởi tạo PDF Converter
    converter = PDFConverter(source_dir, dest_dir)
    
    # Xử lý tất cả các file PDF trong thư mục nguồn
    logger.info("Bắt đầu chuyển đổi các file PDF sang TXT")
    converter.process_all_pdfs()
    
    # Nếu không có danh sách từ khóa, lấy từ cơ sở dữ liệu
    if not keywords_list:
        with app.app_context():
            keywords_list = [keyword.keyword for keyword in Keyword.query.all()]
    
    if not keywords_list:
        logger.warning("Không có từ khóa để tìm kiếm")
        return
    
    logger.info(f"Sẽ tìm kiếm {len(keywords_list)} từ khóa")
    
    # Khởi tạo Keyword Extractor
    extractor = KeywordExtractor(keywords_list)
    
    # Tìm tất cả file TXT trong thư mục nguồn
    txt_files = [f for f in os.listdir(source_dir) 
               if f.lower().endswith('.txt') and 
               os.path.isfile(os.path.join(source_dir, f))]
    
    if not txt_files:
        logger.warning("Không có file TXT để tìm kiếm từ khóa")
        return
    
    logger.info(f"Tìm thấy {len(txt_files)} file TXT để tìm kiếm")
    
    # Lưu trữ kết quả
    all_results = {}
    
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
            
            # Lưu kết quả tìm kiếm
            matches_count = sum(len(matches) for matches in keyword_matches.values())
            logger.info(f"Tìm thấy {matches_count} kết quả cho {len(keyword_matches)} từ khóa trong {txt_file}")
            
            all_results[txt_file] = keyword_matches
            
            # Lưu kết quả vào cơ sở dữ liệu
            with app.app_context():
                # Kiểm tra xem file đã được xử lý chưa
                from models import ProcessedFile, KeywordMatch
                processed_file = ProcessedFile.query.filter_by(file_name=txt_file).first()
                
                if not processed_file:
                    processed_file = ProcessedFile(
                        file_name=txt_file,
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
                            file_name=txt_file,
                            content=match_content
                        )
                        db.session.add(keyword_match)
                
                db.session.commit()
                logger.info(f"Đã lưu kết quả tìm kiếm cho {txt_file} vào cơ sở dữ liệu")
            
        except Exception as e:
            logger.error(f"Lỗi khi xử lý file {txt_file}: {e}")
    
    logger.info("Quá trình xử lý đã hoàn tất")
    return all_results

if __name__ == "__main__":
    # Nếu có danh sách từ khóa từ dòng lệnh, sử dụng nó
    keywords = None
    if len(sys.argv) > 1:
        # Đọc từ khóa từ file
        keywords_file = sys.argv[1]
        try:
            with open(keywords_file, 'r', encoding='utf-8') as f:
                keywords = [line.strip() for line in f if line.strip()]
            logger.info(f"Đã đọc {len(keywords)} từ khóa từ file {keywords_file}")
        except Exception as e:
            logger.error(f"Không thể đọc file từ khóa {keywords_file}: {e}")
            sys.exit(1)
    
    process_pdf_with_keywords(keywords)