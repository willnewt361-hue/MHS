"""
WSGI Entry Point for Production
For use with Gunicorn, uWSGI, or similar production servers

Usage:
    gunicorn --workers 4 --worker-class eventlet -b 0.0.0.0:5000 wsgi:app
"""

import os
import logging
from flask_app import create_app, socketio

# Set environment
os.environ.setdefault('FLASK_ENV', 'production')

# Create app
app = Flask(__name__, static_folder="static", static_url="")
app, socketio = create_app(os.getenv('FLASK_ENV', 'production'))

# Configure logging for production
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/mengo-hub.log',
        maxBytes=10240000,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Mengo-Hub production server started')

if __name__ == '__main__':
    socketio.run(app)
