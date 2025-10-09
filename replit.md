# Soliq.uz QR Fayl Bot

## Overview

This is a Telegram bot that allows users to upload files and receive QR codes for easy sharing and access. When users upload files (PDF, Word, Excel, images, archives), the bot stores them, generates a permanent download link, and creates a QR code that points to the file. The system is designed for the Uzbek market ("soliq.uz" domain) and provides a simple file-sharing workflow through Telegram.

## Recent Changes (October 2025)

- **Admin Panel & Permission System** (Latest - Oct 9, 2025):
  - Added SQLite database (bot_database.db) with users and files tables
  - Implemented permission-based access control system
  - Admin panel accessible via /admin command (admin-only)
  - User detail screen with "Ruxsat berish" and "Rad etish" buttons
  - Automatic notification to users when permission is granted/revoked
  - Admin can view all users, files, and statistics
  - All file uploads tracked in database with metadata
  - @require_permission decorator protects all bot functions
- **UI/UX Improvements** (Oct 9, 2025):
  - Streamlined main keyboard to show only 4 core action buttons
  - Removed "Bot haqida" (About) and "Aloqa" (Contact) from main menu
  - All mode screens now show only "Back" button for cleaner navigation
  - Consistent back-button-only interface in all error and success messages
- **PDF ↔ Word Conversion**: Added bidirectional file conversion between PDF and Word formats
  - PDF → Word using pdf2docx library (preserves layout, images, tables)
  - Word → PDF using LibreOffice headless mode
  - Proper error handling and temporary file cleanup
- **QR Code Embedding**: Embed QR codes directly inside Word and PDF documents
  - Word: Accepts DOCX/DOC files, adds QR on last page (right-aligned, 1x1 inch)
  - PDF: Accepts PDF files, adds QR on last page (bottom-right corner, 1x1 inch)
  - Footer text: "DIDOX.UZ Orqali tasdiqlandi!"
  - QR code points to permanent download link of the file itself

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Architecture (Telegram Integration)
- **Framework**: Python Telegram Bot library (`python-telegram-bot`)
- **Interaction Model**: Inline keyboard-based navigation with callback handlers
- **Command Structure**: 
  - `/start` command initializes the bot with main menu
  - Callback handlers for menu navigation (upload, about, contact)
  - Message handlers for file processing
- **Language**: User interface in Uzbek language
- **File Processing Flow**:
  1. User uploads file through Telegram
  2. Bot validates file type and size (max 20MB)
  3. File is saved with UUID-based naming for uniqueness
  4. QR code is generated pointing to file URL
  5. Both download link and QR code image are sent to user

### File Storage System
- **Local Storage**: Files stored in `uploads/` directory
- **QR Codes**: Generated and stored in `qr_codes/` directory
- **Naming Convention**: UUID-based filenames to prevent conflicts and ensure uniqueness
- **Allowed File Types**: PDF, DOCX, DOC, XLSX, XLS, JPG, JPEG, PNG, GIF, BMP, ZIP, RAR, 7Z, TXT, PPTX, PPT
- **Size Limit**: 20MB maximum file size

### Web Server Architecture
- **Framework**: Flask (lightweight Python web framework)
- **File Serving**: Static file serving from `uploads/` directory
- **Routes**:
  - `/` - Landing page with branding
  - `/files/<filename>` - Direct file download endpoint
- **URL Generation**: Dynamic base URL detection using REPLIT_DEV_DOMAIN environment variable with localhost fallback
- **Download Headers**: Files served with `as_attachment=True` for forced download

### QR Code Generation
- **Library**: `qrcode` Python library
- **Content**: QR codes encode direct file download URLs
- **Format**: PNG images stored locally and sent via Telegram
- **Use Case**: Users can scan QR code with any QR reader to access the file

### Deployment Environment
- **Platform**: Designed for Replit deployment
- **Environment Detection**: Automatic URL configuration based on Replit environment variables
- **Dual Process**: Requires running both Flask server (file_server.py) and Telegram bot (bot.py) concurrently

## External Dependencies

### Telegram Bot API
- **Purpose**: Main interface for user interaction
- **Authentication**: Requires Telegram Bot Token (to be configured)
- **Features Used**: 
  - Message handling
  - File uploads/downloads
  - Inline keyboards
  - Callback queries

### Python Libraries
- **python-telegram-bot**: Telegram bot framework and API wrapper
- **Flask**: Web server for file hosting
- **qrcode**: QR code generation
- **Pillow** (implied): Image processing for QR codes

### Database System
- **Type**: SQLite database (bot_database.db)
- **Tables**:
  - `users`: Stores user_id, username, full_name, is_allowed (permission), created_at
  - `files`: Stores file metadata (filename, path, url, type, size, uploaded_by, uploaded_at)
- **Functions** (database.py):
  - `add_or_update_user()`: Auto-save/update user info on every interaction
  - `is_user_allowed()`: Check if user has permission to use bot
  - `set_user_permission()`: Grant/revoke user access
  - `get_all_users()`: Retrieve all registered users
  - `add_file_record()`: Save file metadata after upload
  - `get_all_files()`: Retrieve all uploaded files
  - `get_stats()`: Get statistics (total users, allowed users, files, storage)

### Permission & Access Control
- **Admin System**: Admin ID stored in ADMIN_TELEGRAM_ID environment secret
- **Permission Decorator**: `@require_permission` protects all bot functions
- **Access Flow**:
  1. User starts bot → auto-saved to database
  2. Permission check → admin always allowed, others need approval
  3. Without permission → error message shown
  4. Admin grants permission → user gets notification
- **Admin Panel** (/admin command):
  - Dashboard with statistics
  - User management: view all users, grant/revoke permissions
  - File management: view all uploaded files with metadata
  - User detail screen with "Ruxsat berish" and "Rad etish" buttons
  - Automatic notifications sent to users on permission change

### File Storage
- **Type**: Local filesystem storage
- **Directories**:
  - `uploads/` - User-uploaded files
  - `qr_codes/` - Generated QR code images
  - `bot_database.db` - SQLite database (gitignored)

### Hosting Platform
- **Primary**: Replit (environment variable detection present)
- **URL Scheme**: HTTPS with dynamic domain from REPLIT_DEV_DOMAIN
- **Fallback**: localhost:5000 for local development

### Future Considerations
- No CDN integration (files served directly from application server)
- No file expiration or cleanup mechanism implemented
- Could add analytics dashboard for admin
- Could implement file search functionality
- Could add bulk operations for admin (delete multiple files, export data)