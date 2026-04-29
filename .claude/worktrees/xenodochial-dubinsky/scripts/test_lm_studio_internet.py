"""
TEST COMPLETO - LM Studio Internet Access
Verifica si LM Studio puede buscar información en internet
"""
import json
import requests
import time
from datetime import datetime

print("\n" + "="*70)
print("🌐 TEST DE ACCESO A INTERNET - LM STUDIO")
print("="*70 + "\n")

# Configuración
LM_STUDIO_URL = "http://172.23.0.1:11434/v1/chat/completions"
MODEL = "qwen2.5-14b-instruct"

# Test queries que REQUIEREN internet
test_cases = [
    {
        "name": "Precio de acción actual",
        "query": "¿Cuál es el precio actual de las acciones de Apple (AAPL)? Dame el precio exacto de hoy.",
        "needs_internet": True,
        "keywords_expected": ["$", "dólar", "precio", "acción", "AAPL"]
    },
    {
        "name": "Noticias recientes",
        "query": "¿Cuáles son las noticias tecnológicas más importantes de esta semana?",
        "needs_internet": True,
        "keywords_expected": ["noticia", "semana", "tecnología", "empresa"]
    },
    {
        "name": "Clima actual",
        "query": "¿Qué temperatura hay ahora en Guadalajara, México?",
        "needs_internet": True,
        "keywords_expected": ["grados", "temperatura", "clima", "°C"]
    },
    {
        "name": "Fecha actual",
        "query": f"¿Qué fecha es hoy? Responde con la fecha exacta. (Hint: hoy es {datetime.now().strftime('%Y-%m-%d')})",
        "needs_internet": False,  # Puede inferirlo del sistema
        "keywords_expected": ["2025", "noviembre", "20"]
    },
    {
        "name": "Conocimiento general",
        "query": "¿Quién es el actual presidente de México en 2025?",
        "needs_internet": False,  # Conocimiento reciente pero puede estar en training
        "keywords_expected": ["Claudia", "Sheinbaum", "presidente", "México"]
    }
]

def call_lm_studio(query):
    """Llama a LM Studio con una query"""
    try:
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "Eres un asistente útil. Si necesitas información actual que no tienes, búscala en internet."},
                {"role": "user", "content": query}
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        response = requests.post(
            LM_STUDIO_URL,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"ERROR: Status {response.status_code}"
            
    except requests.exceptions.Timeout:
        return "ERROR: Timeout"
    except Exception as e:
        return f"ERROR: {str(e)}"

def analyze_response(response, test_case):
    """Analiza si la respuesta parece tener información actual"""
    response_lower = response.lower()
    
    # Check por disclaimers de no tener acceso a internet
    no_internet_phrases = [
        "no tengo acceso",
        "no puedo acceder",
        "no tengo conexión",
        "no puedo buscar",
        "información hasta",
        "cutoff",
        "knowledge cutoff",
        "no tengo datos actuales",
        "no puedo proporcionar información en tiempo real"
    ]
    
    has_disclaimer = any(phrase in response_lower for phrase in no_internet_phrases)
    
    # Check por keywords esperados
    has_expected_content = any(kw.lower() in response_lower for kw in test_case['keywords_expected'])
    
    # Determinar resultado
    if has_disclaimer:
        return "❌ NO INTERNET", "Admite no tener acceso a información actual"
    elif has_expected_content and test_case['needs_internet']:
        return "✅ POSIBLE INTERNET", "Responde con información específica"
    elif has_expected_content and not test_case['needs_internet']:
        return "✅ CONOCIMIENTO", "Responde desde su training data"
    else:
        return "⚠️  INCIERTO", "Respuesta ambigua o incompleta"

# Ejecutar tests
print("⏳ Ejecutando tests...\n")
results = []

for i, test in enumerate(test_cases, 1):
    print(f"📝 Test {i}/{len(test_cases)}: {test['name']}")
    print(f"   Query: {test['query'][:60]}...")
    
    start_time = time.time()
    response = call_lm_studio(test['query'])
    elapsed = time.time() - start_time
    
    if response.startswith("ERROR"):
        print(f"   ❌ {response}")
        results.append({
            "test": test['name'],
            "status": "ERROR",
            "result": "❌ FAILED",
            "time": elapsed
        })
    else:
        status, reason = analyze_response(response, test)
        print(f"   {status}: {reason}")
        print(f"   Tiempo: {elapsed:.1f}s")
        print(f"   Respuesta: {response[:100]}...")
        
        results.append({
            "test": test['name'],
            "status": status,
            "reason": reason,
            "response": response,
            "time": elapsed
        })
    
    print()

# Resumen final
print("="*70)
print("📊 RESUMEN DE RESULTADOS")
print("="*70 + "\n")

internet_tests = [r for r in results if "POSIBLE INTERNET" in r['status']]
no_internet_tests = [r for r in results if "NO INTERNET" in r['status']]
knowledge_tests = [r for r in results if "CONOCIMIENTO" in r['status']]
uncertain_tests = [r for r in results if "INCIERTO" in r['status']]

print(f"✅ Tests con posible internet:  {len(internet_tests)}")
print(f"❌ Tests sin internet:          {len(no_internet_tests)}")
print(f"📚 Tests con conocimiento:      {len(knowledge_tests)}")
print(f"⚠️  Tests inciertos:             {len(uncertain_tests)}")

print("\n" + "="*70)
print("🎯 CONCLUSIÓN")
print("="*70 + "\n")

if len(internet_tests) >= 2:
    print("✅ LM STUDIO PARECE TENER ACCESO A INTERNET")
    print("   Responde con información específica y actual.")
    print("\n💡 RECOMENDACIÓN:")
    print("   Puedes usar LM Studio en el Interview Copilot")
    print("   para búsquedas de información actual.\n")
elif len(no_internet_tests) >= 3:
    print("❌ LM STUDIO NO TIENE ACCESO A INTERNET")
    print("   Solo responde desde su training data.")
    print("\n💡 RECOMENDACIÓN:")
    print("   Usa Gemini API como fallback para información actual.")
    print("   O configura un modelo con internet access (MCP tools).\n")
else:
    print("⚠️  RESULTADO NO CONCLUYENTE")
    print("   Se necesitan más tests para confirmar.")
    print("\n💡 RECOMENDACIÓN:")
    print("   Ejecuta tests manuales con queries específicas")
    print("   que requieran información muy reciente.\n")

# Guardar resultados
with open("logs/lm_studio_internet_test.json", "w", encoding="utf-8") as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "summary": {
            "internet": len(internet_tests),
            "no_internet": len(no_internet_tests),
            "knowledge": len(knowledge_tests),
            "uncertain": len(uncertain_tests)
        }
    }, f, indent=2, ensure_ascii=False)

print("📁 Resultados guardados en: logs/lm_studio_internet_test.json\n")
