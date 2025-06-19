#!/usr/bin/env python3
"""
Error handlers for the application
"""

import logging
from flask import jsonify

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Register error handlers with the Flask app"""
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({'error': 'Internal server error'}), 500

    @app.errorhandler(413)
    def too_large(error):
        """Handle file too large errors."""
        return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

    @app.errorhandler(400)
    def bad_request(error):
        """Handle bad request errors."""
        return jsonify({'error': 'Bad request'}), 400 