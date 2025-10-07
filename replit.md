# Soliq.uz QR Fayl Bot

## Overview

This is a Telegram bot that allows users to upload files and receive QR codes for easy sharing and access. When users upload files (PDF, Word, Excel, images, archives), the bot stores them, generates a permanent download link, and creates a QR code that points to the file. The system is designed for the Uzbek market ("soliq.uz" domain) and provides a simple file-sharing workflow through Telegram.

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

### File Storage
- **Type**: Local filesystem storage
- **Directories**:
  - `uploads/` - User-uploaded files
  - `qr_codes/` - Generated QR code images
- **Note**: No database currently implemented; file metadata tracked through filesystem

### Hosting Platform
- **Primary**: Replit (environment variable detection present)
- **URL Scheme**: HTTPS with dynamic domain from REPLIT_DEV_DOMAIN
- **Fallback**: localhost:5000 for local development

### Future Considerations
- No database integration currently (could be added for file metadata, usage analytics, user tracking)
- No CDN integration (files served directly from application server)
- No authentication/authorization system (bot is open to all Telegram users)
- No file expiration or cleanup mechanism implemented