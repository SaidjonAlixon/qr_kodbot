import os
from flask import Flask, send_from_directory, abort

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/files/<filename>')
def serve_file(filename):
    """Serve uploaded files"""
    try:
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

@app.route('/')
def home():
    """Home page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Soliq.uz - Fayl Xizmati</title>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                text-align: center;
                padding: 40px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                backdrop-filter: blur(10px);
            }
            h1 {
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Soliq.uz - Fayl Xizmati</h1>
            <p>Telegram botimiz orqali fayllarni yuklang va QR kod oling</p>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
