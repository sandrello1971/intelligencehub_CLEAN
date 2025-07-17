"""
Script per integrare Web Scraping V2 nel main.py
"""

INTEGRATION_CODE = '''
# Web Scraping V2 Integration
try:
    from app.services.web_scraping_v2.api_routes import router as web_scraping_v2_router
    from app.services.web_scraping_v2.migrate_db import migrate_database
    
    # Run migration
    migrate_database()
    
    # Include router
    app.include_router(web_scraping_v2_router)
    print("✅ Web Scraping V2 loaded successfully!")
    
except Exception as e:
    print(f"⚠️ Web Scraping V2 failed to load: {e}")
'''

def add_integration():
    """Aggiunge integrazione al main.py"""
    main_py_path = "/var/www/intelligence/backend/app/main.py"
    
    try:
        with open(main_py_path, 'r') as f:
            content = f.read()
        
        # Check if already integrated
        if "web_scraping_v2" in content:
            print("✅ Web Scraping V2 already integrated")
            return True
        
        # Add integration before the last lines
        lines = content.split('\n')
        insert_position = -3  # Before final lines
        
        integration_lines = INTEGRATION_CODE.strip().split('\n')
        for i, line in enumerate(integration_lines):
            lines.insert(insert_position + i, line)
        
        # Write back
        with open(main_py_path, 'w') as f:
            f.write('\n'.join(lines))
        
        print("✅ Web Scraping V2 integration added to main.py")
        return True
        
    except Exception as e:
        print(f"❌ Integration failed: {e}")
        return False

if __name__ == "__main__":
    add_integration()
