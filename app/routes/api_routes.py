#!/usr/bin/env python3
"""
API routes for programmatic access
"""

import os
import logging
from datetime import datetime
from flask import jsonify, request, current_app
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from app.routes import api_bp
from app.services.docx_checker import DocxChecker
from app.utils.file_utils import allowed_file
from app.config import Config

logger = logging.getLogger(__name__)

@api_bp.route('/check', methods=['POST'])
def api_check():
    """API endpoint for file checking."""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only .docx files are allowed.'}), 400
        
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
            
            return jsonify(report.to_dict())
            
        except Exception as e:
            logger.error(f"Error processing file {filename}: {str(e)}")
            # Clean up uploaded file
            try:
                os.remove(filepath)
            except OSError:
                pass
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
            
    except RequestEntityTooLarge:
        return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/health')
def health_check():
    """Health check endpoint for load balancers."""
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }) 