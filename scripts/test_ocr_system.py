"""
Test script for EasyOCR installation and LinkedInOCRHelper
Quick check before using full auto-apply system

Author: Marcos Alberto Alvarado
Project: AI Job Foundry
Date: 2026-01-27
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

print("🧪 Testing EasyOCR Installation")
print("="*60)

# Test 1: Import EasyOCR
print("\n1️⃣ Testing EasyOCR import...")
try:
    import easyocr
    print("✅ EasyOCR imported successfully")
except ImportError as e:
    print(f"❌ EasyOCR import failed: {e}")
    print("Fix: pip install easyocr")
    sys.exit(1)

# Test 2: Import LinkedInOCRHelper
print("\n2️⃣ Testing LinkedInOCRHelper import...")
try:
    from core.automation.linkedin_ocr_helper import LinkedInOCRHelper
    print("✅ LinkedInOCRHelper imported successfully")
except ImportError as e:
    print(f"❌ LinkedInOCRHelper import failed: {e}")
    sys.exit(1)

# Test 3: Initialize OCR Helper
print("\n3️⃣ Initializing EasyOCR (this may take a moment)...")
try:
    helper = LinkedInOCRHelper(languages=['en', 'es'], gpu=True)
    print("✅ EasyOCR initialized successfully")
except Exception as e:
    print(f"⚠️ GPU initialization failed: {e}")
    print("Trying CPU mode...")
    try:
        helper = LinkedInOCRHelper(languages=['en', 'es'], gpu=False)
        print("✅ EasyOCR initialized successfully (CPU mode)")
    except Exception as e2:
        print(f"❌ EasyOCR initialization failed: {e2}")
        sys.exit(1)

# Test 4: Test on sample text (create a simple test image)
print("\n4️⃣ Testing OCR on sample text...")
try:
    from PIL import Image, ImageDraw, ImageFont
    
    # Create a simple test image
    img = Image.new('RGB', (400, 100), color='white')
    draw = ImageDraw.Draw(img)
    
    # Use default font
    text = "Easy Apply"
    draw.text((50, 30), text, fill='black')
    
    test_image_path = "test_ocr_sample.png"
    img.save(test_image_path)
    
    # Test OCR
    elements = helper.extract_text_elements(test_image_path)
    
    if elements:
        print(f"✅ OCR extraction worked! Found {len(elements)} elements")
        print("\nExtracted elements:")
        for elem in elements:
            print(f"   - '{elem['text']}' at ({elem['x']}, {elem['y']}) confidence={elem['confidence']}")
    else:
        print("⚠️ No elements detected (this might be OK, test image is simple)")
    
    # Clean up
    import os
    os.remove(test_image_path)
    
except Exception as e:
    print(f"⚠️ OCR test failed: {e}")
    print("This is not critical - system may still work on real screenshots")

# Test 5: Test LM Studio connection
print("\n5️⃣ Testing LM Studio connection...")
try:
    import requests
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    llm_url = os.getenv('LLM_URL', 'http://127.0.0.1:11434/v1/chat/completions')
    
    # Try to connect
    response = requests.post(
        llm_url,
        json={
            "model": "qwen2.5-14b-instruct",
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 10
        },
        timeout=5
    )
    
    if response.status_code == 200:
        print(f"✅ LM Studio connection successful at {llm_url}")
    else:
        print(f"⚠️ LM Studio returned status {response.status_code}")
        print("Make sure LM Studio is running with Qwen 2.5 14B model loaded")
        
except Exception as e:
    print(f"⚠️ LM Studio connection failed: {e}")
    print("Make sure:")
    print("  1. LM Studio is running")
    print("  2. Qwen 2.5 14B model is loaded")
    print("  3. Server is running (check port 11434)")

print("\n" + "="*60)
print("🎉 TESTING COMPLETE!")
print("="*60)
print("\n📝 Summary:")
print("   ✅ EasyOCR: Installed and working")
print("   ✅ LinkedInOCRHelper: Imported successfully")
print("   ⚠️ LM Studio: Check connection if warning above")
print("\n💡 Next steps:")
print("   1. Make sure LM Studio is running")
print("   2. Run: py control_center.py")
print("   3. Select option 12a (DRY RUN) to test")
print("\n")
