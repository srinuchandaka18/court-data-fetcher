from flask import Flask, render_template, request, jsonify, send_file
import os
import time
import re
from scraper import CourtScraper
from database import DatabaseManager
from config import Config
import requests
from io import BytesIO
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
           template_folder='../frontend/templates', 
           static_folder='../frontend/static')
app.config.from_object(Config)

# Initialize components
db_manager = DatabaseManager(app.config['DATABASE_PATH'])

# Global scraper instance
scraper = None

def get_scraper():
    """Get scraper instance (with demo mode for now)"""
    global scraper
    if scraper is None:
        # Use demo mode until we get the real scraper working
        scraper = CourtScraper(demo_mode=True)
    return scraper

@app.route('/')
def index():
    """Render the main search form"""
    try:
        recent_queries = db_manager.get_recent_queries(5)
        return render_template('index.html', recent_queries=recent_queries)
    except Exception as e:
        logger.error(f"Index page error: {str(e)}")
        return render_template('index.html', recent_queries=[])

@app.route('/search', methods=['POST'])
def search_case():
    """Handle case search requests"""
    query_id = None
    
    try:
        # Get and validate form data
        case_type = request.form.get('case_type', '').strip()
        case_number = request.form.get('case_number', '').strip()
        filing_year = request.form.get('filing_year', '').strip()
        
        # Input validation
        if not all([case_type, case_number, filing_year]):
            return jsonify({"error": "All fields are required"}), 400
        
        try:
            filing_year = int(filing_year)
            current_year = time.gmtime().tm_year
            if filing_year < 1950 or filing_year > current_year:
                return jsonify({"error": "Invalid filing year"}), 400
        except ValueError:
            return jsonify({"error": "Filing year must be a number"}), 400
        
        # Sanitize case number
        if not re.match(r'^[0-9A-Za-z/-]+$', case_number):
            return jsonify({"error": "Invalid case number format"}), 400
        
        logger.info(f"Processing search: {case_type} {case_number}/{filing_year}")
        
        # Log the query
        query_id = db_manager.log_query(case_type, case_number, filing_year)
        
        # Perform search
        court_scraper = get_scraper()
        result = court_scraper.search_case(case_type, case_number, filing_year)
        
        if "error" in result:
            db_manager.update_query_status(query_id, 'failed', error_message=result["error"])
            return jsonify(result), 400
        
        # Save successful result
        db_manager.save_case_details(
            query_id,
            result.get("parties_names"),
            result.get("filing_date"), 
            result.get("next_hearing_date"),
            result.get("case_status"),
            result.get("pdf_links", []),
            result.get("additional_info", {})
        )
        
        db_manager.update_query_status(query_id, 'success')
        
        return jsonify({
            "success": True,
            "data": {
                "parties_names": result.get("parties_names"),
                "filing_date": result.get("filing_date"),
                "next_hearing_date": result.get("next_hearing_date"),
                "case_status": result.get("case_status"),
                "pdf_links": result.get("pdf_links", []),
                "search_duration": result.get("search_duration", 0)
            }
        })
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        if query_id:
            db_manager.update_query_status(query_id, 'failed', error_message=str(e))
        return jsonify({"error": "Server error. Please try again."}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "mode": "demo"})

@app.route('/download_pdf')
def download_pdf():
    """Proxy PDF downloads to avoid CORS issues"""
    pdf_url = request.args.get('url')
    if not pdf_url:
        return jsonify({"error": "No URL provided"}), 400
    
    # For demo mode, return a message since these are example URLs
    if 'example.com' in pdf_url:
        return jsonify({
            "message": "This is a demo PDF link. In production, this would download the actual court document.",
            "demo_url": pdf_url
        }), 200
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(pdf_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        return send_file(
            BytesIO(response.content),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='court_document.pdf'
        )
        
    except Exception as e:
        logger.error(f"PDF download failed: {str(e)}")
        return jsonify({"error": f"Download failed: {str(e)}"}), 500


if __name__ == '__main__':
    print("🚀 Starting Court Data Fetcher...")
    print("📍 Mode: DEMO (using simulated data)")
    print("🌐 Server: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
