# Mengo-Hub - Local HTTPS Setup Guide

## Generate Self-Signed SSL Certificate

### Windows - Using OpenSSL

```batch
# Install OpenSSL if not already installed
# From: https://slproweb.com/products/Win32OpenSSL.html

# Generate self-signed certificate (valid for 365 days)
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 ^
  -subj "/C=UG/ST=Kampala/L=Kampala/O=Mengo-Hub/CN=localhost"

# This creates:
# - cert.pem (certificate file)
# - key.pem (private key file)
```

### Linux/Mac

```bash
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 \
  -subj "/C=UG/ST=Kampala/L=Kampala/O=Mengo-Hub/CN=localhost"
```

---

## Configure Flask for HTTPS

### Update flask_app.py

Add to the bottom before `app.run()`:

```python
import ssl

if __name__ == '__main__':
    # Check if SSL certificates exist
    cert_path = 'cert.pem'
    key_path = 'key.pem'
    
    if os.path.exists(cert_path) and os.path.exists(key_path):
        # Run with SSL
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(cert_path, key_path)
        init_db()
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            ssl_context=ssl_context,
            threaded=True
        )
    else:
        # Run without SSL if certificates not found
        print("⚠️  SSL certificates not found. Running on HTTP.")
        print(f"   Run: openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365")
        init_db()
        app.run(debug=True, host='0.0.0.0', port=5000)
```

---

## Run Local HTTPS Server

### Create run_local_https.bat (Windows)

```batch
@echo off
echo ========================================
echo Mengo-Hub - Local HTTPS Server
echo ========================================
echo.

REM Check if certificates exist
if not exist "cert.pem" (
    echo [!] SSL certificates not found!
    echo Creating self-signed certificates...
    openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 ^
      -subj "/C=UG/ST=Kampala/L=Kampala/O=Mengo-Hub/CN=localhost"
    echo [✓] Certificates created
    echo.
)

REM Install dependencies
echo [*] Installing dependencies...
pip install -r requirements.txt
echo.

REM Run the server
echo [*] Starting Mengo-Hub on https://localhost:5000
echo [!] Ignore SSL certificate warning - this is a self-signed certificate
echo.
python flask_app.py

pause
```

### Create run_local_https.sh (Linux/Mac)

```bash
#!/bin/bash

echo "========================================"
echo "Mengo-Hub - Local HTTPS Server"
echo "========================================"
echo ""

# Check if certificates exist
if [ ! -f "cert.pem" ] || [ ! -f "key.pem" ]; then
    echo "[!] SSL certificates not found!"
    echo "Creating self-signed certificates..."
    openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 \
      -subj "/C=UG/ST=Kampala/L=Kampala/O=Mengo-Hub/CN=localhost"
    echo "[✓] Certificates created"
    echo ""
fi

# Install dependencies
echo "[*] Installing dependencies..."
pip install -r requirements.txt
echo ""

# Run the server
echo "[*] Starting Mengo-Hub on https://localhost:5000"
echo "[!] Ignore SSL certificate warning - this is a self-signed certificate"
echo ""
python flask_app.py
```

---

## Access Mengo-Hub Locally

### URLs
- **Web Interface**: https://localhost:5000/
- **API**: https://localhost:5000/api/

### Browser Warnings
When you visit `https://localhost:5000/`, you'll see a security warning:

**Chrome/Edge/Firefox**:
1. Click "Advanced"
2. Click "Proceed to localhost"

This is normal for self-signed certificates and safe for local development.

---

## Configure NGINX for Local HTTPS (Optional)

### Update nginx.conf

```nginx
upstream mengo_hub {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name localhost;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name localhost;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass https://mengo_hub;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Access NGINX HTTPS

```bash
# Restart NGINX
sudo systemctl restart nginx

# Or on Windows
nginx -s reload
```

Then access: `https://localhost/`

---

## Environment Variables for HTTPS

Add to .env:

```
FLASK_ENV=development
FLASK_DEBUG=True
HTTPS=True
SSL_CERT=cert.pem
SSL_KEY=key.pem
```

---

## Troubleshooting

### Issue: "Connection refused"
- Ensure Flask app is running
- Check port 5000 is not in use: `netstat -ano | findstr :5000`

### Issue: "Certificate verification failed"
- This is normal! Click "Advanced" and proceed
- Or import certificate into system certificate store

### Issue: "Port 5000 already in use"
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process (get PID from above)
taskkill /PID <PID> /F
```

### Issue: "OpenSSL command not found"
- Install OpenSSL: https://slproweb.com/products/Win32OpenSSL.html
- Add to PATH environment variable

---

## Security Notes

⚠️ **Self-signed certificates are only for local development!**

For production, use:
- **Let's Encrypt** (free, automatic renewal)
- **Commercial CA** (GlobalSign, DigiCert, etc.)
- **AWS Certificate Manager** (if using AWS)

---

## Production HTTPS Setup

### Using Let's Encrypt with Certbot

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d mengo-hub.com

# Certificate stored in: /etc/letsencrypt/live/mengo-hub.com/
```

### Update nginx.conf for Production

```nginx
server {
    listen 443 ssl http2;
    server_name mengo-hub.com;

    ssl_certificate /etc/letsencrypt/live/mengo-hub.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mengo-hub.com/privkey.pem;
    
    # ... rest of config
}
```

---

## Next Steps

1. Generate certificates: `openssl req -x509 -newkey rsa:4096 -nodes ...`
2. Run local server: `run_local_https.bat` (Windows) or `run_local_https.sh` (Linux)
3. Access: `https://localhost:5000/`
4. Accept SSL warning
5. Enjoy secure local development!

For production deployment, use Let's Encrypt or commercial certificates.
