#!/bin/bash
# Mengo-Hub System Restructuring Script
# Reorganizes the system into production-ready format

# Create directory structure
mkdir -p app/{routes,models,services,templates,static/{css,js,images,students,teachers},utils}
mkdir -p backups exports receipts logs migrations

echo "✅ Directory structure created!"

# Move service files to app/services/
mv analytics_service.py app/services/
mv admin_service.py app/services/
mv media_service.py app/services/
mv dashboard_service.py app/services/
mv audio_service.py app/services/
mv document_service.py app/services/
mv chat_service.py app/services/
mv assessment_service.py app/services/
mv payment_service.py app/services/
mv certification_service.py app/services/
mv email_service.py app/services/
mv ai_service.py app/services/
mv premium_features.py app/services/

echo "✅ Services organized!"

# Move templates
mv templates/* app/templates/ 2>/dev/null || true

# Move static files
mv public/images/* app/static/images/ 2>/dev/null || true
mv public/images/students/* app/static/students/ 2>/dev/null || true
mv public/images/teachers/* app/static/teachers/ 2>/dev/null || true

echo "✅ Templates and static files organized!"

# Move utilities
mv utilities/* app/utils/ 2>/dev/null || true
mv websocket_ai.py app/utils/
mv premium_routes.py app/utils/

echo "✅ Utilities organized!"

# Move database files
mv schema.sql migrations/
mv populate_db.py migrations/

echo "✅ Migrations organized!"

# Copy data backup
cp -r data/* backups/ 2>/dev/null || true

echo "✅ Backups created!"

# Move configuration files to root if not present
[ ! -f config.py ] && touch config.py
[ ! -f wsgi.py ] && touch wsgi.py
[ ! -f run.py ] && touch run.py

echo "✅ Configuration files created!"

echo "
🎉 RESTRUCTURING COMPLETE!

New Structure:
Mengo-Hub-System/
├── app/
│   ├── routes/           (12 blueprint files)
│   ├── models/           (Database models)
│   ├── services/         (13 service modules)
│   ├── templates/        (HTML templates)
│   ├── static/           (CSS, JS, images)
│   └── utils/            (Helper functions)
├── backups/              (Database backups)
├── exports/              (Report exports)
├── receipts/             (Payment receipts)
├── logs/                 (Application logs)
├── migrations/           (Database migrations)
├── .env                  (Environment variables)
├── config.py             (Configuration)
├── requirements.txt      (Dependencies)
├── run.py                (Development entry point)
└── wsgi.py               (Production entry point)
"
