#!/usr/bin/env python3
import sys
sys.path.append('/var/www/intelligence/backend')
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print('🧪 TEST JOIN SEMPLIFICATO')
print('=' * 30)

# Verifica valori attuali
result1 = db.execute(text('SELECT company_id FROM activities WHERE crm_activity_id = 724246')).fetchone()
print(f'activities.company_id: {result1[0]} (tipo: {type(result1[0])})')

result2 = db.execute(text("SELECT id, name FROM companies WHERE name LIKE '%Ducati%'")).fetchone()
if result2:
    print(f'companies.id: {result2[0]} (tipo: {type(result2[0])}), name: {result2[1]}')

# Test JOIN
company_id = result1[0]
print(f'\nTest JOIN con company_id: {company_id}')

# Test cast integer
query = text('SELECT name FROM companies WHERE id = :company_id')
result = db.execute(query, {'company_id': company_id}).fetchone()

if result:
    print(f'✅ JOIN funziona: "{result[0]}"')
else:
    print('❌ JOIN non funziona')

db.close()
