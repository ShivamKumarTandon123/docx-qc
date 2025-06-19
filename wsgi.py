#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""

import os
from app import create_app
from app.config import config

# Get environment configuration
env = os.environ.get('FLASK_ENV', 'development')
app = create_app(config[env])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 