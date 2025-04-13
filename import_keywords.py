import os
import sys
from app import app, db
from models import Keyword

def import_keywords_from_file(file_path):
    """Import keywords from a text file into the database"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            keywords = [line.strip() for line in f.readlines() if line.strip()]
        
        print(f"Found {len(keywords)} keywords to import")
        
        # Use app context for database operations
        with app.app_context():
            for keyword in keywords:
                try:
                    # Check if keyword already exists
                    existing = Keyword.query.filter_by(keyword=keyword).first()
                    if existing:
                        print(f"Keyword already exists: {keyword}")
                        continue
                    
                    # Create new keyword
                    new_keyword = Keyword(keyword=keyword)
                    db.session.add(new_keyword)
                    db.session.commit()
                    print(f"Added keyword: {keyword}")
                except Exception as e:
                    db.session.rollback()
                    print(f"Error adding keyword '{keyword}': {e}")
                    
        print("Import completed")
    except Exception as e:
        print(f"Error importing keywords: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Default file path or from arguments
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = os.path.join(current_dir, "keywords.txt")
        
    import_keywords_from_file(file_path)