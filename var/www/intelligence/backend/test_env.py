#!/usr/bin/env python3
import os
import sys

print("🔍 TEST CARICAMENTO VARIABILI D'AMBIENTE")
print("=" * 50)

# 1. Verifica variabili d'ambiente sistema
print("1. Variabili d'ambiente sistema:")
system_openai_key = os.environ.get('OPENAI_API_KEY')
print(f"   OPENAI_API_KEY (sistema): {'***' + system_openai_key[-10:] if system_openai_key else 'NON TROVATA'}")

# 2. Carica dotenv
try:
    from dotenv import load_dotenv
    print("\n2. Caricamento file .env:")
    
    # Carica dal file .env nella directory corrente
    load_dotenv()
    dotenv_key = os.getenv('OPENAI_API_KEY')
    print(f"   OPENAI_API_KEY (dopo load_dotenv): {'***' + dotenv_key[-10:] if dotenv_key else 'NON TROVATA'}")
    
    # Carica esplicitamente dal path completo
    load_dotenv('/var/www/intelligence/backend/.env')
    explicit_key = os.getenv('OPENAI_API_KEY')
    print(f"   OPENAI_API_KEY (path esplicito): {'***' + explicit_key[-10:] if explicit_key else 'NON TROVATA'}")
    
except ImportError:
    print("   ❌ python-dotenv non installato")
    explicit_key = None

# 3. Test manuale lettura file .env
print("\n3. Lettura manuale file .env:")
try:
    with open('/var/www/intelligence/backend/.env', 'r') as f:
        for line in f:
            if line.startswith('OPENAI_API_KEY='):
                manual_key = line.strip().split('=', 1)[1]
                print(f"   OPENAI_API_KEY (lettura manuale): {'***' + manual_key[-10:] if manual_key else 'NON TROVATA'}")
                # Imposta manualmente
                os.environ['OPENAI_API_KEY'] = manual_key
                break
except Exception as e:
    print(f"   ❌ Errore lettura file: {e}")

# 4. Test OpenAI
print("\n4. Test OpenAI API:")
final_key = os.getenv('OPENAI_API_KEY')
if final_key:
    try:
        import openai
        client = openai.OpenAI(api_key=final_key)
        
        print("   📡 Tentativo chiamata OpenAI...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Rispondi solo 'OK' per testare l'API"}],
            max_tokens=5
        )
        print("   ✅ OpenAI API funziona correttamente!")
        print(f"   Risposta: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"   ❌ Errore OpenAI: {e}")
        print(f"   Dettaglio errore: {type(e).__name__}")
else:
    print("   ❌ OPENAI_API_KEY non disponibile per il test")

print("\n" + "=" * 50)
print("🏁 Test completato!")
