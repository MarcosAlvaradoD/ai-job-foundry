"""
TEST AI WORKBENCHES - Verificar qué IAs están activas
Basado en tus contenedores Docker
"""

import requests
import json

def test_litellm_router(port=4000):
    """Prueba el router LiteLLM"""
    print("\n🔧 Probando LiteLLM Router...")
    try:
        url = f"http://localhost:{port}/health"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print(f"  ✅ LiteLLM activo en puerto {port}")
            
            # Probar modelos disponibles
            models_url = f"http://localhost:{port}/models"
            models_response = requests.get(models_url, timeout=5)
            if models_response.status_code == 200:
                models = models_response.json()
                print(f"  📋 Modelos disponibles: {len(models.get('data', []))}")
                for model in models.get('data', [])[:5]:
                    print(f"     - {model.get('id', 'unknown')}")
            
            return True
        else:
            print(f"  ⚠️  LiteLLM respondió con status {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print(f"  ❌ LiteLLM no responde en puerto {port}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_n8n(port=5678):
    """Prueba n8n workbench"""
    print("\n⚙️  Probando n8n...")
    try:
        url = f"http://localhost:{port}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print(f"  ✅ n8n activo en puerto {port}")
            print(f"     Abre: http://localhost:{port}")
            return True
        else:
            print(f"  ⚠️  n8n respondió con status {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print(f"  ❌ n8n no responde en puerto {port}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_plane(port=8080):
    """Prueba Plane project management"""
    print("\n📋 Probando Plane...")
    try:
        url = f"http://localhost:{port}/sign-up"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print(f"  ✅ Plane activo en puerto {port}")
            print(f"     Abre: http://localhost:{port}")
            return True
        else:
            print(f"  ⚠️  Plane respondió con status {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Plane no responde en puerto {port}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_minio(port=5901):
    """Prueba MinIO object storage"""
    print("\n🗄️  Probando MinIO...")
    try:
        url = f"http://localhost:{port}/browser"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print(f"  ✅ MinIO activo en puerto {port}")
            print(f"     Abre: http://localhost:{port}/browser")
            return True
        else:
            print(f"  ⚠️  MinIO respondió con status {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print(f"  ❌ MinIO no responde en puerto {port}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_lm_studio(port=1234):
    """Prueba LM Studio (modelo local)"""
    print("\n🤖 Probando LM Studio...")
    try:
        url = f"http://localhost:{port}/v1/models"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print(f"  ✅ LM Studio activo en puerto {port}")
            models = response.json()
            
            if 'data' in models and models['data']:
                print(f"  📋 Modelo cargado: {models['data'][0].get('id', 'unknown')}")
            else:
                print(f"  ⚠️  Sin modelos cargados")
            
            return True
        else:
            print(f"  ⚠️  LM Studio respondió con status {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print(f"  ❌ LM Studio no responde en puerto {port}")
        print(f"     ¿Está LM Studio abierto?")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_ai_completion(port=1234):
    """Prueba generar una respuesta con IA"""
    print("\n💬 Probando generación de texto...")
    
    try:
        url = f"http://localhost:{port}/v1/chat/completions"
        
        payload = {
            "model": "local-model",
            "messages": [
                {"role": "user", "content": "Responde con una sola palabra: ¿Estás funcionando?"}
            ],
            "temperature": 0.7,
            "max_tokens": 50
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            answer = result['choices'][0]['message']['content']
            print(f"  ✅ IA respondió: '{answer}'")
            return True
        else:
            print(f"  ⚠️  Error {response.status_code}")
            return False
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  🧪 TEST DE INFRAESTRUCTURA AI")
    print("="*60)
    
    results = {
        "LM Studio": test_lm_studio(),
        "LiteLLM Router": test_litellm_router(),
        "n8n": test_n8n(),
        "Plane": test_plane(),
        "MinIO": test_minio()
    }
    
    # Probar generación de texto si LM Studio funciona
    if results["LM Studio"]:
        results["AI Completion"] = test_ai_completion()
    
    print("\n" + "="*60)
    print("  📊 RESUMEN")
    print("="*60 + "\n")
    
    for service, status in results.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {service}")
    
    active = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n  Total: {active}/{total} servicios activos")
    
    if results.get("LM Studio") and results.get("AI Completion"):
        print("\n  🎉 ¡Tu IA local está funcionando!")
        print("     Puedes usarla para el Interview Copilot")
    else:
        print("\n  ⚠️  Necesitas activar LM Studio para usar IA local")
        print("     O usa OpenAI/Gemini API en su lugar")
    
    print()

if __name__ == "__main__":
    main()