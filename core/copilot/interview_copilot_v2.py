"""
INTERVIEW COPILOT V2 - CON JOB CONTEXT
Versión mejorada que incluye información de la vacante

NUEVO:
✅ Job Context Injection - Información de la vacante en el prompt
✅ Company Research - Contexto de la empresa
✅ Role-specific prep - Preparación específica del rol
✅ Integration con Google Sheets - Carga job info automática

USO:
1. python interview_copilot_v2.py
2. Selecciona job de la lista (o ingresa manualmente)
3. Sistema carga: CV + Job Info + Company Context
4. Push-to-talk: Ctrl+Shift+R para grabar
5. 'summary' al final para resumen completo
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json

# Add core to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.sheets.sheet_manager import SheetManager
from core.copilot.interview_copilot_session_recorder import InterviewSessionRecorder

class InterviewCopilotV2(InterviewSessionRecorder):
    """
    Interview Copilot V2 con Job Context
    """
    
    def __init__(self, cv_path: str = "data/cv_descriptor.txt"):
        super().__init__(cv_path)
        self.sheet_manager = SheetManager()
        self.job_context = None
        self.company_context = None
        
    def load_job_from_sheets(self, row_id: int = None, fit_score_min: int = 7):
        """
        Carga información de job desde Google Sheets
        
        Args:
            row_id: ID específico del job
            fit_score_min: Score mínimo para filtrar
        
        Returns:
            Job dict o None
        """
        print("\n📊 Cargando jobs desde Google Sheets...")
        
        try:
            jobs = self.sheet_manager.get_all_jobs()
            
            if not jobs:
                print("❌ No se encontraron jobs en Sheets")
                return None
            
            # Filtrar por FIT score
            high_fit_jobs = [j for j in jobs if j.get('FitScore', 0) >= fit_score_min]
            
            if not high_fit_jobs:
                print(f"❌ No hay jobs con FIT >= {fit_score_min}")
                return None
            
            # Si hay row_id específico, buscarlo
            if row_id:
                job = next((j for j in high_fit_jobs if j.get('row_id') == row_id), None)
                if job:
                    return job
                else:
                    print(f"❌ Job {row_id} no encontrado")
                    return None
            
            # Mostrar lista de jobs
            print(f"\n✅ {len(high_fit_jobs)} jobs con FIT >= {fit_score_min}:\n")
            for i, job in enumerate(high_fit_jobs[:10], 1):  # Top 10
                company = job.get('Company', 'Unknown')
                role = job.get('Role', 'Unknown')
                fit = job.get('FitScore', 0)
                print(f"{i}. [{fit}/10] {company} - {role}")
            
            # Seleccionar job
            while True:
                try:
                    choice = input("\n📝 Selecciona el número del job (1-10) o 0 para ingresar manualmente: ")
                    choice = int(choice)
                    
                    if choice == 0:
                        return None  # Ingreso manual
                    elif 1 <= choice <= len(high_fit_jobs):
                        return high_fit_jobs[choice - 1]
                    else:
                        print("❌ Número inválido")
                except ValueError:
                    print("❌ Ingresa un número válido")
        
        except Exception as e:
            print(f"❌ Error cargando jobs: {e}")
            return None
    
    def set_job_context_manual(self):
        """
        Permite ingresar job context manualmente
        """
        print("\n📝 INGRESO MANUAL DE JOB CONTEXT")
        print("="*60)
        
        company = input("Empresa: ").strip()
        role = input("Rol/Posición: ").strip()
        location = input("Ubicación (opcional): ").strip()
        
        print("\n📋 Descripción del job (multi-línea, termina con línea vacía):")
        description_lines = []
        while True:
            line = input()
            if not line:
                break
            description_lines.append(line)
        
        description = "\n".join(description_lines)
        
        print("\n📋 Requisitos clave (separados por comas):")
        requirements = input().strip()
        
        print("\n💰 Salario/Compensación (opcional):")
        compensation = input().strip()
        
        self.job_context = {
            "Company": company,
            "Role": role,
            "Location": location,
            "Description": description,
            "Requirements": requirements,
            "Compensation": compensation,
            "Source": "Manual Entry"
        }
        
        print("\n✅ Job context guardado")
    
    def set_job_context_from_dict(self, job: dict):
        """
        Configura job context desde un dict (Google Sheets)
        """
        self.job_context = {
            "Company": job.get('Company', 'Unknown'),
            "Role": job.get('Role', 'Unknown'),
            "Location": job.get('Location', 'Unknown'),
            "RemoteScope": job.get('RemoteScope', 'Unknown'),
            "FitScore": job.get('FitScore', 0),
            "Why": job.get('Why', ''),
            "Seniority": job.get('Seniority', 'Unknown'),
            "ApplyURL": job.get('ApplyURL', ''),
            "Source": job.get('Source', 'Unknown'),
            "Requirements": "Ver descripción completa en el link",
            "Notes": job.get('Notes', '')
        }
        
        print(f"\n✅ Job context cargado: {self.job_context['Company']} - {self.job_context['Role']}")
    
    def generate_company_context(self):
        """
        Genera contexto de la empresa usando AI
        """
        if not self.job_context:
            return
        
        company_name = self.job_context.get('Company', '')
        if not company_name or company_name == 'Unknown':
            return
        
        print(f"\n🔍 Generando contexto de empresa: {company_name}...")
        
        prompt = f"""
Genera un resumen ejecutivo sobre la empresa {company_name} para preparación de entrevista.

Incluye:
1. Industria y sector
2. Tamaño y presencia global
3. Productos/servicios principales
4. Cultura y valores
5. Noticias recientes relevantes

Resumen (máx 300 palabras):
"""
        
        try:
            if self.llm:
                response = self.llm.complete(prompt, system_prompt="Eres un research assistant que ayuda a preparar entrevistas.")
                self.company_context = response
                print("✅ Company context generado")
            else:
                print("⚠️  LLM no disponible, skip company research")
        except Exception as e:
            print(f"❌ Error generando company context: {e}")
    
    def get_system_prompt(self) -> str:
        """
        Genera system prompt CON job context
        """
        base_prompt = """Eres un asistente de entrevistas experto. Tu rol es:

1. Escuchar preguntas/situaciones de la entrevista
2. Sugerir respuestas basadas en el CV y experiencia del candidato
3. Dar consejos STAR (Situación, Tarea, Acción, Resultado)
4. Mantener respuestas concisas y relevantes

IMPORTANTE:
- Responde en 2-3 oraciones máximo
- Enfócate en ejemplos concretos del CV
- Usa formato STAR para behavioral questions
"""
        
        if self.cv_content:
            base_prompt += f"\n\n📄 CV DEL CANDIDATO:\n{self.cv_content[:2000]}\n"
        
        if self.job_context:
            job_info = f"""
📋 JOB AL QUE APLICA:
- Empresa: {self.job_context.get('Company', 'N/A')}
- Rol: {self.job_context.get('Role', 'N/A')}
- Ubicación: {self.job_context.get('Location', 'N/A')}
- Remote: {self.job_context.get('RemoteScope', 'N/A')}
- FIT Score: {self.job_context.get('FitScore', 'N/A')}/10
- Por qué buen match: {self.job_context.get('Why', 'N/A')}
- Seniority: {self.job_context.get('Seniority', 'N/A')}
"""
            base_prompt += job_info
        
        if self.company_context:
            base_prompt += f"\n\n🏢 CONTEXTO DE LA EMPRESA:\n{self.company_context[:500]}\n"
        
        base_prompt += """
\n💡 ENFOCA TUS RESPUESTAS EN:
- Alinear experiencia del CV con requisitos del job
- Destacar projects relevantes
- Mencionar el FIT score alto y por qué
- Mostrar interés genuino en la empresa
"""
        
        return base_prompt
    
    def display_job_summary(self):
        """
        Muestra resumen de job context configurado
        """
        if not self.job_context:
            print("\n⚠️  No hay job context configurado")
            return
        
        print("\n" + "="*60)
        print("📋 JOB CONTEXT CONFIGURADO")
        print("="*60)
        print(f"Empresa:     {self.job_context.get('Company')}")
        print(f"Rol:         {self.job_context.get('Role')}")
        print(f"Ubicación:   {self.job_context.get('Location')}")
        print(f"Remote:      {self.job_context.get('RemoteScope', 'N/A')}")
        print(f"FIT Score:   {self.job_context.get('FitScore', 'N/A')}/10")
        print(f"Fuente:      {self.job_context.get('Source')}")
        
        if self.job_context.get('Why'):
            print(f"\n💡 Por qué buen match:")
            print(f"   {self.job_context.get('Why')[:200]}...")
        
        if self.company_context:
            print(f"\n🏢 Company Research: ✅ Disponible")
        
        print("="*60 + "\n")

def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🎤 INTERVIEW COPILOT V2 - CON JOB CONTEXT")
    print("="*60 + "\n")
    
    # Inicializar copilot
    copilot = InterviewCopilotV2()
    
    # Configurar job context
    print("📊 CONFIGURACIÓN DE JOB CONTEXT\n")
    print("Opciones:")
    print("1. Cargar desde Google Sheets (recomendado)")
    print("2. Ingreso manual")
    print("3. Skip (solo usar CV)")
    
    choice = input("\nSelecciona (1-3): ").strip()
    
    if choice == "1":
        job = copilot.load_job_from_sheets()
        if job:
            copilot.set_job_context_from_dict(job)
            copilot.generate_company_context()
        else:
            print("\n⚠️  No se cargó job, ¿ingresar manualmente? (y/n)")
            if input().lower() == 'y':
                copilot.set_job_context_manual()
    
    elif choice == "2":
        copilot.set_job_context_manual()
        copilot.generate_company_context()
    
    else:
        print("\n⚠️  Continuando sin job context (solo CV)")
    
    # Mostrar resumen
    copilot.display_job_summary()
    
    # Iniciar sesión
    print("\n✅ COPILOT LISTO")
    print("\n📝 INSTRUCCIONES:")
    print("   - Ctrl+Shift+R: MANTÉN presionado para grabar")
    print("   - 'summary': Obtener resumen final")
    print("   - 'quit': Salir\n")
    
    input("Presiona Enter para iniciar sesión...")
    
    # Aquí continúa el loop de la sesión
    # (usa el código del InterviewSessionRecorder original)
    print("\n🎤 Sesión iniciada - Usa Ctrl+Shift+R para grabar\n")
    
    # TODO: Implementar loop de sesión con el nuevo system prompt
    # Por ahora solo mostramos que está listo
    
    print("\n⚠️  NOTA: Loop de sesión pendiente de implementación completa")
    print("   El sistema prompt con job context está configurado ✅")
    print("   Usa copilot.get_system_prompt() para obtenerlo\n")

if __name__ == "__main__":
    main()
