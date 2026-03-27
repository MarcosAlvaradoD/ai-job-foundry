#!/usr/bin/env python3
"""
AUTO-MODIFICA: job_bulletin_processor.py
Agrega soporte para Adzuna, Computrabajo, JobLeads
"""
import re

FILE_PATH = r"C:\Users\MSI\Desktop\ai-job-foundry\core\automation\job_bulletin_processor.py"

print(f"Modificando: {FILE_PATH}\n")

# Read file
with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# ========================================
# 1. UPDATE detect_bulletin_type()
# ========================================
print("1️⃣ Actualizando detect_bulletin_type()...")

# Find the method
detect_method_pattern = r'(def detect_bulletin_type\(self, sender: str, subject: str\):.*?)(return None)'

new_detection_code = r'''\1
        # ✅ NUEVO: Adzuna
        if 'no-reply@adzuna.com' in sender_lower or 'adzuna' in sender_lower:
            if 'vacante' in subject_lower or 'empleos similares' in subject_lower:
                return 'adzuna'
        
        # ✅ NUEVO: Computrabajo
        if 'computrabajo' in sender_lower or 'alertas@computrabajo.com' in sender_lower:
            if 'perfect match' in subject_lower or 'resumen' in subject_lower or 'empleos' in subject_lower:
                return 'computrabajo'
        
        # ✅ NUEVO: JobLeads
        if 'jobleads.com' in sender_lower or 'mailer@jobleads.com' in sender_lower:
            if 'trabajo' in subject_lower or 'coinciden' in subject_lower:
                return 'jobleads'
        
        \2'''

content = re.sub(detect_method_pattern, new_detection_code, content, flags=re.DOTALL)

print("  ✅ detect_bulletin_type() actualizado")

# ========================================
# 2. UPDATE Gmail query
# ========================================
print("2️⃣ Actualizando Gmail query...")

old_query = r'''query = \(
\s*'from:\(noreply@glassdoor\.com OR jobs-noreply@linkedin\.com OR noreply@indeed\.com\) '
\s*'subject:\(empleos OR jobs OR "nuevos empleos" OR "new jobs" OR postúlate OR apply\) '
\s*'newer_than:7d'
\s*\)'''

new_query = '''query = (
            'from:(noreply@glassdoor.com OR jobs-noreply@linkedin.com OR noreply@indeed.com '
            'OR no-reply@adzuna.com OR alertas@computrabajo.com OR mailer@jobleads.com) '
            'subject:(empleos OR jobs OR "nuevos empleos" OR "new jobs" OR postúlate OR apply '
            'OR vacante OR "perfect match" OR coinciden) '
            'newer_than:7d'
        )'''

content = re.sub(old_query, new_query, content, flags=re.MULTILINE | re.DOTALL)

print("  ✅ Gmail query actualizado")

# ========================================
# 3. UPDATE process_bulletins() to handle new types
# ========================================
print("3️⃣ Actualizando process_bulletins()...")

# Find where glassdoor jobs are extracted
glassdoor_extract_pattern = r"(elif bulletin_type == 'glassdoor':.*?jobs = self\.extract_glassdoor_jobs\(html_content\))"

new_handlers = r'''\1
            
            elif bulletin_type == 'adzuna':
                print("   🤖 Using AI parser for Adzuna bulletin...")
                jobs = self.ai_email_parser.extract_jobs_from_html(html_content, source='Adzuna')
            
            elif bulletin_type == 'computrabajo':
                print("   🤖 Using AI parser for Computrabajo bulletin...")
                jobs = self.ai_email_parser.extract_jobs_from_html(html_content, source='Computrabajo')
            
            elif bulletin_type == 'jobleads':
                print("   🤖 Using AI parser for JobLeads bulletin...")
                jobs = self.ai_email_parser.extract_jobs_from_html(html_content, source='JobLeads')'''

content = re.sub(glassdoor_extract_pattern, new_handlers, content, flags=re.DOTALL)

print("  ✅ process_bulletins() actualizado")

# ========================================
# Write back
# ========================================
with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "="*70)
print("✅ MODIFICACIÓN COMPLETADA")
print("="*70)
print("\nCambios realizados:")
print("  1. ✅ detect_bulletin_type() reconoce Adzuna/Computrabajo/JobLeads")
print("  2. ✅ Gmail query incluye nuevos senders")
print("  3. ✅ process_bulletins() usa AI parser para nuevos boletines")
print("\nPróxima ejecución del pipeline procesará los nuevos boletines.")
print("="*70)
