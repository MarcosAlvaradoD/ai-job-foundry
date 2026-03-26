"""
AI JOB FOUNDRY - LinkedIn Credentials Helper
Obtiene credenciales de LinkedIn desde .env
"""

import os
from dotenv import load_dotenv
from pathlib import Path

def get_linkedin_credentials():
    """
    Obtiene credenciales de LinkedIn desde variables de entorno
    
    Returns:
        tuple: (email, password)
    """
    # Load .env
    env_path = Path(__file__).parent.parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
    
    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")
    
    if not email or not password:
        raise ValueError("LINKEDIN_EMAIL and LINKEDIN_PASSWORD must be set in .env")
    
    return email, password