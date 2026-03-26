#!/usr/bin/env python3
"""
AI Job Analyzer - Wrapper simplificado para analyze_board.py
Calcula FIT scores usando LLM local (LM Studio)
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

LLM_URL = os.getenv("LLM_URL", "http://127.0.0.1:11434/v1/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5-14b-instruct")

class AIAnalyzer:
    """Analizador de jobs con IA"""
    
    def __init__(self):
        self.llm_url = LLM_URL
        self.llm_model = LLM_MODEL
    
    def analyze_job(self, job_data: dict) -> dict:
        """
        Analiza un job y retorna FIT score + razón
        
        Args:
            job_data: {
                'Role': str,
                'Company': str,
                'ApplyURL': str,
                'full_description': str
            }
        
        Returns:
            {
                'fit_score': int (0-10),
                'why': str,
                'seniority': str
            }
        """
        role = job_data.get('Role', 'Unknown')
        company = job_data.get('Company', 'Unknown')
        description = job_data.get('full_description', '')
        
        # Prompt para el LLM
        prompt = f"""Eres un experto en análisis de ofertas laborales para Marcos Alvarado.

PERFIL DE MARCOS:
- Project Manager / IT Manager senior
- 10+ años experiencia
- Especializado en: ERP migrations (Dynamics AX, SAP), ETL, BI/Power BI, LATAM projects
- NO busca: Software Developer/Programmer roles
- Prioridad: Remote work

OFERTA A ANALIZAR:
Título: {role}
Empresa: {company}
Descripción: {description[:1000]}

INSTRUCCIONES:
Calcula un FIT SCORE del 0 al 10:
- 0-3: No match (developer, junior, presencial obligatorio)
- 4-6: Medio (algunas skills coinciden)
- 7-8: Buen match (PM/BA/IT Manager, buenas skills)
- 9-10: Excelente match (PM Senior, LATAM, remoto, ERP/ETL)

Responde SOLO en este formato JSON:
{{
  "fit_score": 8,
  "why": "Razón breve (max 100 palabras)",
  "seniority": "Mid-Level | Senior | Lead"
}}"""
        
        try:
            # Llamar al LLM
            response = requests.post(
                self.llm_url,
                json={
                    "model": self.llm_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 300
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return self._default_response()
            
            content = response.json()['choices'][0]['message']['content']
            
            # Parse JSON response
            import json
            # Remove markdown if present
            content = content.replace('```json', '').replace('```', '').strip()
            result = json.loads(content)
            
            return {
                'fit_score': min(10, max(0, int(result.get('fit_score', 5)))),
                'why': result.get('why', 'Analysis completed'),
                'seniority': result.get('seniority', 'Unknown')
            }
            
        except Exception as e:
            print(f"  ⚠️  Error en análisis IA: {e}")
            return self._default_response()
    
    def _default_response(self) -> dict:
        """Response por defecto si falla el LLM"""
        return {
            'fit_score': 5,
            'why': 'Unable to analyze - LLM error',
            'seniority': 'Unknown'
        }
