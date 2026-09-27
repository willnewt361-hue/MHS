#!/bin/bash
# Mengo-Hub Production Deployment Script
# Run this script on your Ubuntu/Debian server

set -e

echo "🚀 Starting Mengo-Hub Production Deployment"

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "📦 Installing required packages..."
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx sqlite3

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /var/www/mengo-hub
sudo chown -R $USER:$USER /var/www/mengo-hub

# Copy application files (assuming they're in current directory)
echo "📋 Copying application files..."
cp -r . /var/www/mengo-hub/
cd /var/www/mengo-hub

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
pip install gunicorn

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "🔧 Creating .env file..."
    cat > .env << EOF
SECRET_KEY=$(openssl rand -hex 32)
ADMIN_SECRET_KEY=Newton2026
ADMIN_SECRET_PASSWORD=2026
ADMIN_API_TOKEN=MengoAdminAPIToken2026
SUPER_ADMIN_API_TOKEN=MengoSuperAdminToken2026
LOGIN_ATTEMPTS_LIMIT=5
LOCKOUT_HOURS=24
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://:password@localhost:5432/mengo_hub

DATABASE=data/mengo.db
FLASK_ENV=production
IMPORT_CSV_PATH=data/import.csv
ADMIN_IMPORT_PASSWORD=ImportPassword2026
PORT=5000
FLASK_ENV=development
DEBUG=False
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EOF
    echo "⚠️  Please edit .env file with your actual SMTP credentials!"
fi

# Initialize database
echo "🗄️  Initializing database..."
python3 populate_db.py

# Configure Nginx
echo "🌐 Configuring Nginx..."
sudo cp nginx.conf /etc/nginx/sites-available/mengo-hub
sudo ln -sf /etc/nginx/sites-available/mengo-hub /etc/nginx/sites-enabled/

# Update nginx configuration with correct paths
sudo sed -i "s|/path/to/your/project|/var/www/mengo-hub|g" /etc/nginx/sites-available/mengo-hub

# Remove default nginx site
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
echo "🧪 Testing Nginx configuration..."
sudo nginx -t

# Configure systemd service
echo "⚙️  Configuring systemd service..."
sudo cp mengo-hub.service /etc/systemd/system/
sudo sed -i "s|/path/to/your/venv|/var/www/mengo-hub/venv|g" /etc/systemd/system/mengo-hub.service
sudo sed -i "s|/path/to/your/mengo-hub-system|/var/www/mengo-hub|g" /etc/systemd/system/mengo-hub.service
sudo sed -i "s|User=www-data|User=$USER|g" /etc/systemd/system/mengo-hub.service
sudo sed -i "s|Group=www-data|Group=$USER|g" /etc/systemd/system/mengo-hub.service

# Set proper permissions
echo "🔒 Setting proper permissions..."
sudo chown -R $USER:$USER /var/www/mengo-hub
sudo chmod -R 755 /var/www/mengo-hub

# Start services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable mengo-hub
sudo systemctl start mengo-hub
sudo systemctl enable nginx
sudo systemctl restart nginx

# Firewall configuration (optional)
echo "🔥 Configuring firewall..."
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

echo "✅ Deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit /var/www/mengo-hub/.env with your SMTP credentials"
echo "2. Run: sudo certbot --nginx -d your-domain.com"
echo "3. Update nginx.conf with your domain name"
echo "4. Restart nginx: sudo systemctl restart nginx"
echo ""
echo "🌐 Your application should be running at http://your-server-ip"
echo "🔒 After SSL setup, it will be available at https://your-domain.com"