#!/usr/bin/env python3
"""
Replit-optimized entry point for Fajar Mandiri Store
Wedding invitation and CV generator web application
"""

import os
import sys
import sqlite3
from datetime import datetime

# Import the Flask app and SocketIO from the main application
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables for Replit compatibility
os.environ.setdefault('FLASK_SECRET_KEY', 'replit-dev-secret-key-change-in-production')

# Import all the necessary components from app.py (copied from app.pyw)
try:
    from app import app, socketio, init_db, USER_DOCS
    print("✓ Successfully imported Flask app and SocketIO")
except ImportError as e:
    print(f"❌ Error importing app components: {e}")
    print("Make sure app.py exists and contains the required components")
    sys.exit(1)

def setup_replit_environment():
    """Setup the application for Replit environment"""
    
    # Ensure the database is properly initialized
    try:
        print("🔧 Initializing database...")
        init_db()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
    
    # Create necessary directories
    directories = [
        USER_DOCS,
        os.path.join(USER_DOCS, 'cv_templates'),
        os.path.join(USER_DOCS, 'wedding_templates'),
        os.path.join(USER_DOCS, 'music'),
        os.path.join(USER_DOCS, 'prewedding_photos'),
        os.path.join(USER_DOCS, 'thumbnails'),
        'static/images',
        'static/images/templates',
        'static/images/wedding_templates'
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            print(f"⚠️  Warning: Could not create directory {directory}: {e}")
    
    print("✓ Directory structure created")

def main():
    """Main entry point for Replit"""
    print("🌸 Starting Fajar Mandiri Store - Wedding Invitation & CV Generator")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Setup environment
    setup_replit_environment()
    
    # Get port from environment (Replit will set this)
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'  # Required for Replit
    
    print(f"🚀 Starting server on {host}:{port}")
    print("🔗 The application will be available through Replit's web preview")
    
    try:
        # Use SocketIO if available, otherwise fallback to Flask
        if hasattr(socketio, 'run') and callable(socketio.run):
            print("📡 Starting with SocketIO support (real-time chat enabled)")
            socketio.run(
                app,
                host=host,
                port=port,
                debug=False,
                use_reloader=False,
                allow_unsafe_werkzeug=True
            )
        else:
            print("📡 Starting with Flask only (no real-time chat)")
            app.run(
                host=host,
                port=port,
                debug=False,
                use_reloader=False
            )
    except Exception as e:
        print(f"❌ Server startup error: {e}")
        print("🔄 Trying fallback Flask server...")
        try:
            app.run(
                host=host,
                port=port,
                debug=True
            )
        except Exception as fallback_error:
            print(f"❌ Fallback server also failed: {fallback_error}")
            sys.exit(1)

if __name__ == "__main__":
    main()