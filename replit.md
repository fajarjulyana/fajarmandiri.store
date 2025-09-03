# Fajar Mandiri Store - Project Setup Documentation

## Project Overview
**Fajar Mandiri Store** is a comprehensive web application for creating wedding invitations and professional CVs with integrated print services and real-time chat support.

### Key Features
- **Wedding Invitations**: 18+ premium templates with customization options
- **CV Generator**: Professional CV templates with multiple designs  
- **Print Services**: Integrated printing for documents, photos, marketing materials
- **Real-time Chat**: Customer support chat with SocketIO
- **User Management**: Google OAuth integration and premium accounts
- **Template Management**: Dynamic template system with thumbnails

## Technical Architecture

### Backend
- **Framework**: Flask 2.3.3 with Flask-SocketIO
- **Database**: SQLite (development), PostgreSQL planned for v2.0
- **Authentication**: Flask-Login + Google OAuth 2.0
- **Real-time**: WebSocket for chat system
- **File Processing**: PIL for images, QR code generation, Selenium for thumbnails

### Frontend
- **Framework**: Bootstrap 5 with jQuery
- **Icons**: FontAwesome 6
- **Mobile**: Responsive design with mobile-first approach
- **PWA**: Progressive Web App capabilities

### Dependencies
- Flask==2.3.3, Werkzeug==2.3.7
- flask-socketio, eventlet (real-time chat)
- google-auth, google-auth-oauthlib (OAuth)
- qrcode[pil], pillow (image processing)
- selenium, webdriver-manager (thumbnails)
- pystray, psutil (desktop app support)

## Replit Configuration

### Environment Setup
- **Python Version**: 3.11
- **Entry Point**: `main.py` (Replit-optimized)
- **Original Desktop App**: `app.pyw` (Windows-focused)
- **Host Binding**: 0.0.0.0:5000 (Replit compatible)
- **Database Location**: ~/Documents/FajarMandiriStore/fajarmandiri.db

### Deployment
- **Type**: Autoscale (stateless web app)
- **Command**: `python main.py`
- **Port**: 5000 (frontend)
- **Features**: SocketIO support, file uploads, database integration

### File Structure
```
├── main.py                 # Replit entry point
├── app.py / app.pyw        # Main Flask application
├── setup_demo_data.py      # Database initialization
├── requirements.txt        # Python dependencies
├── static/                 # CSS, JS, images
├── templates/              # Jinja2 HTML templates
├── config/                 # App configuration
└── ~/Documents/FajarMandiriStore/  # Data directory
    ├── fajarmandiri.db     # SQLite database
    ├── wedding_templates/   # Template files
    ├── cv_templates/       # CV templates
    ├── prewedding_photos/  # User uploads
    └── thumbnails/         # Generated previews
```

## Recent Changes (Import Setup)

### ✅ Completed Tasks
1. **Python Environment**: Installed Python 3.11 with all dependencies
2. **Database Setup**: Initialized SQLite database with demo data
3. **Replit Adaptation**: Created `main.py` entry point for cloud deployment
4. **Port Configuration**: Modified from 5001 to 5000 for Replit compatibility
5. **Workflow Setup**: Configured Flask app to run with SocketIO support
6. **Deployment Config**: Set up autoscale deployment for production

### 🔧 Modifications Made
- **Host Binding**: Changed from desktop app to cloud-compatible (0.0.0.0:5000)
- **Import System**: Created `app.py` copy from `app.pyw` for proper module imports
- **Environment Variables**: Added Replit-compatible secret key defaults
- **Directory Structure**: Ensured all required directories are created on startup
- **Error Handling**: Added graceful fallbacks for SocketIO initialization

### 🎯 Current Status
- ✅ **Server Running**: Flask app with SocketIO support active on port 5000
- ✅ **Database Active**: SQLite database with demo wedding invitation data
- ✅ **Templates Working**: Wedding invitation templates accessible
- ✅ **Chat System**: Real-time chat widget loaded and functional
- ✅ **Deployment Ready**: Configured for Replit autoscale deployment

## User Preferences
- **Development Style**: Maintain existing architecture and conventions
- **Database**: Keep SQLite for development (PostgreSQL migration planned v2.0)
- **Features**: Preserve all original functionality (wedding invitations, CV generator, chat, printing)
- **UI/UX**: Maintain existing Bootstrap-based responsive design

## Future Considerations
- **Database Migration**: Plan PostgreSQL upgrade for production scaling
- **Template Storage**: Consider cloud storage for production deployment
- **Performance**: Monitor chat system performance under load
- **Security**: Review file upload security and OAuth implementation

---
**Last Updated**: 2025-09-02
**Status**: Import Completed - Ready for Development/Production