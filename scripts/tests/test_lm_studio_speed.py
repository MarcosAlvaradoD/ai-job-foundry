"""
Test rápido de velocidad de LM Studio con Llama-3-Groq-70B

Mide el tiempo de respuesta para un job simple y diagnostica problemas.

Usage:
    py scripts\\tests\\test_lm_studio_speed.py
"""

import os
import sys
import time
import requests
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment
from dotenv import load_dotenv
load_dotenv()

LLM_URL = os.getenv("LLM_URL", "http://127.0.0.1:11434/v1/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3-groq-70b-tool-use")

def test_speed():
    """Test LLM speed with a simple job analysis."""
    
    print("\n" + "="*80)
    print("🚀 LM STUDIO SPEED TEST")
    print("="*80)
    
    print(f"\n📍 Configuration:")
    print(f"   URL: {LLM_URL}")
    print(f"   Model: {LLM_MODEL}")
    
    # Simple test prompt
    prompt = """Analyze this job match.

JOB:
- Role: Senior Product Manager
- Company: Tech Startup
- Location: Remote
- Requirements: 5+ years PM experience, B2B SaaS, Agile

CANDIDATE:
- 10+ years PM/PO experience
- ERP migrations, BI/Power BI
- Multinational project management
- Scrum, PMBOK, Lean Six Sigma

Return ONLY JSON:
{
  "fit": <0-100>,
  "why": "<brief explanation>"
}"""

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "Return only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4,
        "stream": False
    }
    
    print("\n⏱️  Testing speed...")
    print("   (This should take 10-15 seconds if optimized)")
    print("   (Or 40-100 seconds if not optimized)")
    
    start_time = time.time()
    
    try:
        response = requests.post(LLM_URL, json=payload, timeout=180)
        response.raise_for_status()
        
        elapsed_time = time.time() - start_time
        
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        
        print("\n✅ Response received!")
        print(f"\n📊 RESULTS:")
        print(f"   Time: {elapsed_time:.1f} seconds")
        print(f"   Content: {content[:100]}...")
        
        # Diagnose speed
        print(f"\n🔍 DIAGNOSIS:")
        if elapsed_time < 20:
            print("   ✅ EXCELLENT - Model is fully optimized!")
            print("   Expected pipeline time: 36-45 minutes (182 jobs)")
        elif elapsed_time < 40:
            print("   ✅ GOOD - Minor optimization possible")
            print("   Expected pipeline time: 1-1.5 hours (182 jobs)")
        elif elapsed_time < 60:
            print("   ⚠️  SLOW - Check LM Studio configuration")
            print("   Expected pipeline time: 1.5-2 hours (182 jobs)")
            print("\n   Recommendations:")
            print("   1. Verify GPU Offload = 21/80 layers")
            print("   2. Enable 'Keep in Memory'")
            print("   3. Check Context Length = 8192")
        else:
            print("   ❌ VERY SLOW - Configuration issue detected")
            print("   Expected pipeline time: 2-5 hours (182 jobs)")
            print("\n   Critical issues:")
            print("   1. GPU Offload may be wrong (check < 21 layers)")
            print("   2. Model may not be in memory")
            print("   3. Context length may be too high")
            print("\n   Consider using Qwen temporarily (15 min total)")
        
        return elapsed_time
        
    except requests.exceptions.Timeout:
        elapsed_time = time.time() - start_time
        print(f"\n❌ TIMEOUT after {elapsed_time:.1f} seconds")
        print("\n🔍 DIAGNOSIS:")
        print("   Model is taking > 3 minutes per job")
        print("   This will result in 9+ hours for full pipeline")
        print("\n   CRITICAL: Check LM Studio configuration")
        print("   Or switch to Qwen temporarily")
        return None
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n🔍 Possible causes:")
        print("   1. LM Studio not running")
        print("   2. Model not loaded")
        print("   3. Wrong URL/port")
        print(f"\n   Check: {LLM_URL}")
        return None


def check_lm_studio_config():
    """Check if LM Studio is reachable."""
    
    print("\n" + "="*80)
    print("🔍 LM STUDIO CONNECTION TEST")
    print("="*80)
    
    try:
        # Try to reach LM Studio
        base_url = LLM_URL.replace("/v1/chat/completions", "")
        response = requests.get(base_url, timeout=5)
        
        print(f"\n✅ LM Studio is reachable at: {base_url}")
        return True
        
    except Exception as e:
        print(f"\n❌ Cannot reach LM Studio at: {base_url}")
        print(f"   Error: {e}")
        print("\n   Solutions:")
        print("   1. Open LM Studio")
        print("   2. Load model: llama-3-groq-70b-tool-use")
        print("   3. Start server (green button)")
        return False


if __name__ == "__main__":
    print("\n🎯 AI JOB FOUNDRY - LM STUDIO SPEED DIAGNOSTIC")
    
    # Step 1: Check connection
    if not check_lm_studio_config():
        print("\n❌ Cannot proceed - LM Studio not running")
        sys.exit(1)
    
    # Step 2: Test speed
    elapsed_time = test_speed()
    
    # Step 3: Summary
    print("\n" + "="*80)
    print("📋 SUMMARY")
    print("="*80)
    
    if elapsed_time:
        estimated_total = (elapsed_time * 182) / 60  # minutes
        print(f"\n   Single job: {elapsed_time:.1f} seconds")
        print(f"   Full pipeline (182 jobs): ~{estimated_total:.0f} minutes")
        
        if estimated_total < 60:
            print(f"\n   ✅ This is acceptable for overnight batch processing")
        elif estimated_total < 120:
            print(f"\n   ⚠️  Consider optimizing LM Studio for better speed")
        else:
            print(f"\n   ❌ Too slow - optimization required or use Qwen")
    else:
        print("\n   ❌ Test failed - check configuration")
    
    print("\n" + "="*80)
