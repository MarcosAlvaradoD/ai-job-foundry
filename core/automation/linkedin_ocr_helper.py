"""
LinkedIn OCR Helper - Extract text and coordinates from screenshots using EasyOCR
100% FREE, LOCAL, NO API COSTS

Author: Marcos Alberto Alvarado
Project: AI Job Foundry
Date: 2026-01-27
"""

import easyocr
from typing import List, Dict, Tuple
from PIL import Image
import numpy as np


class LinkedInOCRHelper:
    """
    Helper class for extracting text and coordinates from LinkedIn pages using EasyOCR
    """
    
    def __init__(self, languages: List[str] = None, gpu: bool = True):
        """
        Initialize EasyOCR reader
        
        Args:
            languages: List of language codes (default: ['en', 'es'])
            gpu: Use GPU if available (default: True)
        """
        if languages is None:
            languages = ['en', 'es']
        
        print(f"🔧 Initializing EasyOCR with languages: {languages}")
        print(f"   GPU: {gpu}")
        
        try:
            self.reader = easyocr.Reader(languages, gpu=gpu)
            print("✅ EasyOCR initialized successfully")
        except Exception as e:
            print(f"⚠️ GPU initialization failed, falling back to CPU: {e}")
            self.reader = easyocr.Reader(languages, gpu=False)
            print("✅ EasyOCR initialized (CPU mode)")
    
    def extract_text_elements(self, image_path: str, min_confidence: float = 0.5) -> List[Dict]:
        """
        Extract text elements with coordinates from an image
        
        Args:
            image_path: Path to screenshot
            min_confidence: Minimum confidence threshold (0.0 to 1.0)
            
        Returns:
            List of dicts with format:
            [
                {
                    "text": "Easy Apply",
                    "confidence": 0.95,
                    "x": 100,
                    "y": 200,
                    "width": 80,
                    "height": 30,
                    "bbox": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                },
                ...
            ]
        """
        try:
            # Read image
            results = self.reader.readtext(image_path)
            
            # Parse results
            elements = []
            for (bbox, text, confidence) in results:
                if confidence >= min_confidence:
                    # Calculate center coordinates
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                    
                    x_min, x_max = min(x_coords), max(x_coords)
                    y_min, y_max = min(y_coords), max(y_coords)
                    
                    x_center = int((x_min + x_max) / 2)
                    y_center = int((y_min + y_max) / 2)
                    width = int(x_max - x_min)
                    height = int(y_max - y_min)
                    
                    elements.append({
                        "text": text,
                        "confidence": round(confidence, 2),
                        "x": x_center,
                        "y": y_center,
                        "width": width,
                        "height": height,
                        "bbox": bbox
                    })
            
            print(f"📸 OCR extracted {len(elements)} elements (confidence >= {min_confidence})")
            return elements
            
        except Exception as e:
            print(f"❌ OCR extraction failed: {e}")
            return []
    
    def find_elements_by_text(self, elements: List[Dict], search_text: str, case_sensitive: bool = False) -> List[Dict]:
        """
        Find elements containing specific text
        
        Args:
            elements: List of extracted elements
            search_text: Text to search for
            case_sensitive: Case-sensitive search
            
        Returns:
            Matching elements
        """
        if not case_sensitive:
            search_text = search_text.lower()
        
        matches = []
        for elem in elements:
            text = elem['text']
            if not case_sensitive:
                text = text.lower()
            
            if search_text in text:
                matches.append(elem)
        
        return matches
    
    def find_buttons(self, elements: List[Dict], button_texts: List[str] = None) -> List[Dict]:
        """
        Find button-like elements by common button texts
        
        Args:
            elements: List of extracted elements
            button_texts: List of button texts to search for
            
        Returns:
            Elements likely to be buttons
        """
        if button_texts is None:
            button_texts = [
                'apply', 'easy apply', 'solicitar', 'enviar', 'siguiente', 
                'next', 'continue', 'submit', 'send', 'save', 'guardar'
            ]
        
        buttons = []
        for elem in elements:
            text_lower = elem['text'].lower()
            for btn_text in button_texts:
                if btn_text in text_lower:
                    buttons.append(elem)
                    break
        
        print(f"🔘 Found {len(buttons)} potential buttons")
        return buttons
    
    def get_element_summary(self, elements: List[Dict], max_elements: int = 50) -> str:
        """
        Get a text summary of extracted elements for LLM analysis
        
        Args:
            elements: List of extracted elements
            max_elements: Maximum elements to include
            
        Returns:
            Formatted string with element info
        """
        summary_lines = []
        for i, elem in enumerate(elements[:max_elements]):
            summary_lines.append(
                f"{i+1}. '{elem['text']}' at ({elem['x']}, {elem['y']}) "
                f"[{elem['width']}x{elem['height']}] conf={elem['confidence']}"
            )
        
        if len(elements) > max_elements:
            summary_lines.append(f"... and {len(elements) - max_elements} more elements")
        
        return "\n".join(summary_lines)


if __name__ == "__main__":
    # Test the OCR helper
    print("🧪 Testing LinkedInOCRHelper")
    
    helper = LinkedInOCRHelper()
    
    # Test on a sample screenshot (you'll need to provide a real one)
    # elements = helper.extract_text_elements("test_screenshot.png")
    # print(helper.get_element_summary(elements))
    
    print("✅ LinkedInOCRHelper initialized successfully")
