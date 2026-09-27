"""
Development Entry Point
Run with: python run.py
"""

import os
import sys
from flask_app import app, socketio
import logging
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging
file_handler = RotatingFileHandler('logs/mengo-hub.log', maxBytes=10240000, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)

# Configure app
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Mengo-Hub startup')

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║  🎓 MENGO-HUB EDUCATIONAL PLATFORM                            ║
    ║  Starting Development Server...                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Check for SSL certificates
    import ssl
    cert_path = 'cert.pem'
    key_path = 'key.pem'
    
    ssl_context = None
    if os.path.exists(cert_path) and os.path.exists(key_path):
        print("✅ SSL certificates found - running on HTTPS")
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(cert_path, key_path)
        socketio.run(app, host='0.0.0.0', port=5000, ssl_context=ssl_context, debug=True)
    else:
        print("⚠️  SSL certificates not found - running on HTTP")
        print("   To enable HTTPS: openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365")
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
