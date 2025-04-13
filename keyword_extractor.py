import re
import os
import logging
from pathlib import Path
from typing import List, Dict, Tuple

class KeywordExtractor:
    """Class for extracting content related to keywords from text files"""
    
    def __init__(self, keywords=None):
        """
        Initialize the Keyword Extractor
        
        Args:
            keywords (List[str], optional): List of keywords to search for
        """
        self.keywords = keywords or []
        self.logger = logging.getLogger(__name__)
        
    def set_keywords(self, keywords: List[str]):
        """
        Set the list of keywords to search for
        
        Args:
            keywords (List[str]): List of keywords
        """
        self.keywords = keywords
        
    def extract_from_text(self, text: str, window_size: int = 500) -> Dict[str, List[str]]:
        """
        Extract content around keywords from text
        
        Args:
            text (str): The text to search in
            window_size (int, optional): Number of characters to include before and after the keyword
            
        Returns:
            Dict[str, List[str]]: Dictionary with keywords as keys and list of extracted content as values
        """
        results = {}
        
        if not self.keywords or not text:
            return results
            
        # Process each keyword
        for keyword in self.keywords:
            results[keyword] = []
            
            # Find all occurrences of the keyword (case insensitive)
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            for match in pattern.finditer(text):
                start_pos = max(0, match.start() - window_size)
                end_pos = min(len(text), match.end() + window_size)
                
                # Extract content around the keyword
                context = text[start_pos:end_pos]
                
                # Add to results
                results[keyword].append(context)
                
        return results
    
    def extract_from_file(self, file_path: str, window_size: int = 500) -> Dict[str, List[str]]:
        """
        Extract content around keywords from a text file
        
        Args:
            file_path (str): Path to the text file
            window_size (int, optional): Number of characters to include before and after the keyword
            
        Returns:
            Dict[str, List[str]]: Dictionary with keywords as keys and list of extracted content as values
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return self.extract_from_text(text, window_size)
        except Exception as e:
            self.logger.error(f"Error extracting keywords from {file_path}: {e}")
            return {}
    
    def extract_from_directory(self, directory: str, file_extension: str = '.txt', window_size: int = 500) -> Dict[str, Dict[str, List[str]]]:
        """
        Extract content around keywords from all text files in a directory
        
        Args:
            directory (str): Path to the directory containing text files
            file_extension (str, optional): File extension to look for
            window_size (int, optional): Number of characters to include before and after the keyword
            
        Returns:
            Dict[str, Dict[str, List[str]]]: Dictionary with file names as keys and extraction results as values
        """
        results = {}
        
        try:
            # Get all text files in the directory
            text_files = [f for f in os.listdir(directory) 
                          if f.lower().endswith(file_extension) and 
                          os.path.isfile(os.path.join(directory, f))]
            
            for text_file in text_files:
                file_path = os.path.join(directory, text_file)
                file_results = self.extract_from_file(file_path, window_size)
                
                if file_results:  # Only add non-empty results
                    results[text_file] = file_results
                    
            return results
        except Exception as e:
            self.logger.error(f"Error processing directory {directory}: {e}")
            return {}