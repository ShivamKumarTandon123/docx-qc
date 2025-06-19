#!/usr/bin/env python3
"""
Main routes for web interface
"""

import os
import logging
from datetime import datetime
from flask import render_template, request, current_app
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from app.routes import main_bp
from app.services.docx_checker import DocxChecker
from app.utils.file_utils import allowed_file
from app.config import Config

logger = logging.getLogger(__name__)

@main_bp.route('/')
def index():
    """Main page with file upload form."""
    return render_template('upload.html')

@main_bp.route('/check', methods=['POST'])
def check_file():
    """Web interface for file checking."""
    try:
        if 'file' not in request.files:
            return render_template('upload.html', error='No file provided')
        
        file = request.files['file']
        if file.filename == '':
            return render_template('upload.html', error='No file selected')
        
        if not allowed_file(file.filename):
            return render_template('upload.html', error='Invalid file type. Only .docx files are allowed.')
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], safe_filename)
        file.save(filepath)
        
        logger.info(f"Processing file: {filename}")
        
        # Run QC checks
        try:
            checker = DocxChecker(filepath, Config())
            report = checker.run_all_checks()
            
            # Clean up uploaded file
            try:
                os.remove(filepath)
            except OSError:
                logger.warning(f"Could not remove temporary file: {filepath}")
            
            return render_template('result.html', result=report.to_dict(), filename=filename)
            
        except Exception as e:
            logger.error(f"Error processing file {filename}: {str(e)}")
            # Clean up uploaded file
            try:
                os.remove(filepath)
            except OSError:
                pass
            return render_template('upload.html', error=f'Error processing file: {str(e)}')
            
    except RequestEntityTooLarge:
        return render_template('upload.html', error='File too large. Maximum size is 16MB.')
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return render_template('upload.html', error='Internal server error') 