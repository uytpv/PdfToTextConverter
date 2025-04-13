import logging
from typing import List, Dict, Optional, Tuple
from models import db, Keyword, KeywordMatch, ProcessedFile

class DatabaseManager:
    """Class for managing database operations related to keyword extraction"""
    
    def __init__(self):
        """Initialize the Database Manager"""
        self.logger = logging.getLogger(__name__)
    
    def add_keyword(self, keyword: str, description: str = None) -> Optional[Keyword]:
        """
        Add a new keyword to the database
        
        Args:
            keyword (str): The keyword to add
            description (str, optional): Description of the keyword
            
        Returns:
            Optional[Keyword]: The created Keyword object or None if error occurs
        """
        try:
            # Check if keyword already exists
            existing = Keyword.query.filter_by(keyword=keyword).first()
            if existing:
                self.logger.info(f"Keyword '{keyword}' already exists.")
                return existing
                
            # Create new keyword
            new_keyword = Keyword(keyword=keyword, description=description)
            db.session.add(new_keyword)
            db.session.commit()
            
            self.logger.info(f"Added new keyword: {keyword}")
            return new_keyword
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error adding keyword '{keyword}': {e}")
            return None
    
    def get_all_keywords(self) -> List[Keyword]:
        """
        Get all keywords from the database
        
        Returns:
            List[Keyword]: List of all Keyword objects
        """
        try:
            return Keyword.query.all()
        except Exception as e:
            self.logger.error(f"Error retrieving keywords: {e}")
            return []
    
    def get_keywords_as_list(self) -> List[str]:
        """
        Get all keywords as a list of strings
        
        Returns:
            List[str]: List of keyword strings
        """
        try:
            keywords = Keyword.query.all()
            return [k.keyword for k in keywords]
        except Exception as e:
            self.logger.error(f"Error retrieving keywords as list: {e}")
            return []
    
    def save_keyword_matches(self, file_name: str, keyword_matches: Dict[str, List[str]]) -> bool:
        """
        Save keyword matches to the database
        
        Args:
            file_name (str): Name of the file that was processed
            keyword_matches (Dict[str, List[str]]): Dictionary with keywords as keys and matches as values
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            for keyword_text, matches in keyword_matches.items():
                # Get keyword object
                keyword = Keyword.query.filter_by(keyword=keyword_text).first()
                
                if not keyword:
                    # Create keyword if it doesn't exist
                    keyword = Keyword(keyword=keyword_text)
                    db.session.add(keyword)
                    db.session.flush()  # Get ID without committing
                
                # Add matches
                for content in matches:
                    match = KeywordMatch(
                        keyword_id=keyword.id,
                        file_name=file_name,
                        content=content
                    )
                    db.session.add(match)
            
            db.session.commit()
            self.logger.info(f"Saved keyword matches for file: {file_name}")
            return True
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error saving keyword matches for file '{file_name}': {e}")
            return False
    
    def mark_file_as_processed(self, file_name: str, file_path: str, status: str = 'processed') -> bool:
        """
        Mark a file as processed in the database
        
        Args:
            file_name (str): Name of the file
            file_path (str): Path to the file
            status (str, optional): Processing status ('processed', 'failed', etc.)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if file is already in database
            existing = ProcessedFile.query.filter_by(file_name=file_name).first()
            
            if existing:
                # Update existing record
                existing.file_path = file_path
                existing.status = status
            else:
                # Create new record
                processed_file = ProcessedFile(
                    file_name=file_name,
                    file_path=file_path,
                    status=status
                )
                db.session.add(processed_file)
            
            db.session.commit()
            self.logger.info(f"Marked file as {status}: {file_name}")
            return True
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error marking file '{file_name}' as processed: {e}")
            return False
    
    def get_keyword_matches(self, keyword: str = None, file_name: str = None) -> List[KeywordMatch]:
        """
        Get keyword matches from the database, optionally filtered by keyword or file name
        
        Args:
            keyword (str, optional): Filter by keyword text
            file_name (str, optional): Filter by file name
            
        Returns:
            List[KeywordMatch]: List of KeywordMatch objects
        """
        try:
            query = KeywordMatch.query
            
            if keyword:
                keyword_obj = Keyword.query.filter_by(keyword=keyword).first()
                if keyword_obj:
                    query = query.filter_by(keyword_id=keyword_obj.id)
                else:
                    return []
                    
            if file_name:
                query = query.filter_by(file_name=file_name)
                
            return query.all()
        except Exception as e:
            self.logger.error(f"Error retrieving keyword matches: {e}")
            return []