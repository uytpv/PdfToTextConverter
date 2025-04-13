import os
import logging
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from models import db, Keyword, KeywordMatch, ProcessedFile
from database_manager import DatabaseManager
from keyword_extractor import KeywordExtractor
from pdf_converter import PDFConverter
from pathlib import Path
from sqlalchemy.exc import IntegrityError, ProgrammingError, OperationalError

# Create Flask application
app = Flask(__name__)

# Configure app
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_key_for_development')

# Initialize database with app
db.init_app(app)

# Create database tables
with app.app_context():
    try:
        # Attempt to create tables - this will handle if tables don't exist yet
        db.create_all()
    except (IntegrityError, ProgrammingError, OperationalError) as e:
        # Log the error but continue - tables likely already exist
        print(f"Note: {str(e)}")
        print("Tables may already exist, continuing...")

# Initialize managers
db_manager = DatabaseManager()
keyword_extractor = KeywordExtractor()

# Define routes
@app.route('/')
def index():
    """Home page with form to add keywords and list of existing keywords"""
    keywords = Keyword.query.all()
    return render_template('index.html', keywords=keywords)

@app.route('/keywords', methods=['GET', 'POST'])
def manage_keywords():
    """Add, edit, or delete keywords"""
    if request.method == 'POST':
        keyword = request.form.get('keyword')
        description = request.form.get('description')
        
        if keyword:
            result = db_manager.add_keyword(keyword, description)
            if result:
                flash(f'Từ khóa "{keyword}" đã được thêm thành công.', 'success')
            else:
                flash(f'Không thể thêm từ khóa "{keyword}".', 'danger')
        
        return redirect(url_for('manage_keywords'))
    
    keywords = Keyword.query.all()
    return render_template('keywords.html', keywords=keywords)

@app.route('/keywords/delete/<int:id>', methods=['POST'])
def delete_keyword(id):
    """Delete a keyword"""
    try:
        keyword = Keyword.query.get_or_404(id)
        db.session.delete(keyword)
        db.session.commit()
        flash(f'Từ khóa "{keyword.keyword}" đã được xóa.', 'success')
    except Exception as e:
        flash(f'Lỗi khi xóa từ khóa: {str(e)}', 'danger')
    
    return redirect(url_for('manage_keywords'))

@app.route('/process', methods=['GET', 'POST'])
def process_files():
    """Process PDF files and extract keywords"""
    if request.method == 'POST':
        # Define source and destination directories
        current_dir = os.path.dirname(os.path.abspath(__file__))
        source_dir = os.path.join(current_dir, "TaiVe")
        dest_dir = os.path.join(current_dir, "TaiVe_Done")
        
        # Create directories if they don't exist
        os.makedirs(source_dir, exist_ok=True)
        os.makedirs(dest_dir, exist_ok=True)
        
        # Initialize converter
        converter = PDFConverter(source_dir, dest_dir)
        
        # Process PDFs
        converter.process_all_pdfs()
        
        # Get all keywords
        keywords = db_manager.get_keywords_as_list()
        keyword_extractor.set_keywords(keywords)
        
        # Extract keywords from text files
        results = keyword_extractor.extract_from_directory(source_dir, '.txt')
        
        # Save results to database
        for file_name, keyword_matches in results.items():
            db_manager.save_keyword_matches(file_name, keyword_matches)
            file_path = os.path.join(source_dir, file_name)
            db_manager.mark_file_as_processed(file_name, file_path)
        
        flash('Quá trình xử lý đã hoàn tất.', 'success')
        return redirect(url_for('view_results'))
    
    return render_template('process.html')

@app.route('/results')
def view_results():
    """View keyword extraction results"""
    keyword_id = request.args.get('keyword_id')
    file_name = request.args.get('file_name')
    
    query = KeywordMatch.query
    
    if keyword_id:
        query = query.filter_by(keyword_id=keyword_id)
    
    if file_name:
        query = query.filter_by(file_name=file_name)
    
    matches = query.all()
    keywords = Keyword.query.all()
    processed_files = ProcessedFile.query.all()
    
    return render_template('results.html', 
                          matches=matches, 
                          keywords=keywords, 
                          processed_files=processed_files,
                          selected_keyword=keyword_id,
                          selected_file=file_name)

# API routes for AJAX calls
@app.route('/api/matches/<int:keyword_id>')
def api_get_matches(keyword_id):
    """Get matches for a specific keyword"""
    matches = KeywordMatch.query.filter_by(keyword_id=keyword_id).all()
    result = []
    
    for match in matches:
        result.append({
            'id': match.id,
            'file_name': match.file_name,
            'content': match.content,
            'created_at': match.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(result)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)