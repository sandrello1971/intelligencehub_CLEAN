#!/bin/bash
set -e
timestamp=$(date +%Y%m%d_%H%M%S)
backup_dir="/var/backups/intelligence_$timestamp"
mkdir -p $backup_dir

# Database backup
PGPASSWORD=intelligence_pass pg_dump -U intelligence_user -h localhost -d intelligence > $backup_dir/intelligence_backup.sql

# Code backup
cp -r /var/www/intelligence/backend $backup_dir/backend_backup

# Working files backup
cp /var/www/intelligence/backend/app/routes/auth.py $backup_dir/auth_working.py
cp /var/www/intelligence/backend/app/schemas/users.py $backup_dir/users_working.py

echo "✅ Recovery backup created: $backup_dir"
