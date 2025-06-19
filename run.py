#!/usr/bin/env python3
"""
Development entry point
"""

import os
import socket
from app import create_app
from app.config import DevelopmentConfig

def find_free_port(start_port=5001, max_attempts=10):
    """Find a free port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return start_port  # Fallback to start_port if no free port found

app = create_app(DevelopmentConfig)

if __name__ == '__main__':
    # Use environment variable for port or find a free port
    port = int(os.environ.get('FLASK_PORT', find_free_port()))
    
    print(f"[INFO] Starting the application...")
    print(f"[INFO] Using port {port}")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=port)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"[ERROR] Port {port} is in use. Trying alternative port...")
            alt_port = find_free_port(port + 1)
            print(f"[INFO] Using alternative port {alt_port}")
            app.run(debug=True, host='0.0.0.0', port=alt_port)
        else:
            raise e 