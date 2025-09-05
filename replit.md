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

## Recent Changes (Database Fixed & Webhook Integration - Completed)

### ✅ All Tasks Completed Successfully
1. **Python Environment**: Installed Python 3.11 with all Flask dependencies
2. **Database Setup**: Initialized SQLite database with demo data and all required tables
3. **Replit Adaptation**: Created `main.py` entry point optimized for cloud deployment
4. **Port Configuration**: Configured for port 5000 with proper host binding (0.0.0.0)
5. **Workflow Setup**: Flask app running with SocketIO support for real-time chat
6. **Syntax Fixes**: Resolved all major syntax errors in app.py for stable operation
7. **Midtrans Integration**: Added secure environment variables for payment processing
8. **Deployment Config**: Set up autoscale deployment for production readiness

### 🔧 Key Modifications Made
- **Database Schema Fixed**: Complete database rebuild with all required tables and columns
- **Template Directory**: Fixed ~/Documents/FajarMandiriStore/ directory structure as intended
- **Midtrans Webhooks**: Added all required webhook endpoints (/payment/finish, /payment/unfinish, /payment/error, /notification/handling)
- **Sandbox Environment**: Switched to Midtrans sandbox for development testing
- **Payment Links**: Updated to sandbox payment links for testing
- **Database Population**: Successfully populated with wedding templates, CV templates, demo data
- **Schema Completion**: Added all missing tables (orders, wedding_guests, print_services, etc.)

### 🎯 Current Status - FULLY OPERATIONAL & FIXED
- ✅ **Server Running**: Flask app with SocketIO support active on port 5000
- ✅ **Database Fixed**: SQLite database with complete schema, all tables, and demo data
- ✅ **Templates Working**: 4 wedding invitation templates + 4 CV templates loaded
- ✅ **Chat System**: Real-time chat widget functional with WebSocket support
- ✅ **Payment System**: Midtrans sandbox integration with webhook endpoints configured
- ✅ **Admin Panel**: Admin dashboard accessible (username: fajar, password: fajar123)
- ✅ **Webhook Integration**: All Midtrans webhook endpoints implemented and working
- ✅ **Directory Structure**: Proper ~/Documents/FajarMandiriStore/ structure maintained
- ✅ **Deployment Ready**: Autoscale deployment configured for production

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

## GitHub Import Setup - Successfully Completed

### ✅ Fresh Import Setup Tasks Completed (2025-09-05)
1. **Environment Setup**: Installed Python 3.11 with all required Flask dependencies
2. **Host Configuration**: Configured Flask app to bind to 0.0.0.0:5000 for Replit proxy compatibility  
3. **Database Initialization**: SQLite database created with complete schema and demo data
4. **Dependency Management**: Cleaned and installed all requirements from requirements.txt
5. **GTK Compatibility**: Made GTK imports optional for cloud deployment compatibility
6. **Midtrans Integration**: Set default values for payment gateway environment variables
7. **Workflow Configuration**: Set up Flask Server workflow with SocketIO support
8. **Deployment Configuration**: Configured autoscale deployment for production readiness

### 🔧 Key Replit Adaptations Made
- **Host Binding**: Changed from localhost to 0.0.0.0:5000 for Replit proxy support
- **Environment Variables**: Made Midtrans payment keys optional with defaults for development
- **GTK Dependencies**: Made Linux desktop GUI components optional for cloud deployment
- **File Structure**: Maintained ~/Documents/FajarMandiriStore/ directory structure as designed
- **Database Path**: Configured SQLite database location for Replit persistent storage
- **Entry Point**: Using main.py as Replit-optimized entry point instead of app.pyw

### 🎯 Current Status - FULLY OPERATIONAL FROM FRESH IMPORT
- ✅ **Server Running**: Flask app with SocketIO support active on port 5000
- ✅ **Database Ready**: SQLite database with complete schema, all tables, and demo data
- ✅ **Templates Loaded**: 4 wedding invitation templates + 4 CV templates available
- ✅ **Chat System**: Real-time chat widget functional with WebSocket support
- ✅ **Payment System**: Midtrans integration configured with development defaults
- ✅ **Admin Panel**: Admin dashboard accessible (username: fajar, password: fajar123)
- ✅ **Demo Data**: Sample wedding invitation created for testing
- ✅ **Directory Structure**: Proper ~/Documents/FajarMandiriStore/ structure established
- ✅ **Deployment Ready**: Autoscale deployment configured for production

---
**Last Updated**: 2025-09-05  
**Version**: v1.8.1 - New Features Preview  
**Status**: Development Version - Approaching Stable v2.0 Release