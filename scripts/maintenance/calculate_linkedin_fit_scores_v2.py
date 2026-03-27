#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculate FIT Scores - WITH RATE LIMIT PROTECTION
Version: 2.0 - Adds delay between writes to avoid 429 errors
"""
import sys
import os
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.enrichment.ai_analyzer import AIAnalyzer
from core.sheets.sheet_manager import SheetManager
from dotenv import load_dotenv

load_dotenv()

def main():
    print("\n" + "="*70)
    print("🎯 CALCULATE FIT SCORES - WITH RATE LIMIT PROTECTION")
    print("="*70)
    
    sheet_id = os.getenv('GOOGLE_SHEETS_ID')
    llm_url = os.getenv('LLM_URL')
    
    print(f"Sheet: {sheet_id}")
    print(f"LLM: {llm_url}")
    print("="*70)
    
    sheet_manager = SheetManager()
    analyzer = AIAnalyzer()
    
    print("\n📊 Reading LinkedIn tab...")
    jobs = sheet_manager.get_all_jobs('linkedin')
    print(f"✅ Found {len(jobs)} total jobs")
    
    # Add row numbers
    for i, job in enumerate(jobs, start=2):
        job['_row'] = i
    
    # Filter jobs without FIT score
    jobs_without_fit = [j for j in jobs if not j.get('FitScore')]
    print(f"\n📋 {len(jobs_without_fit)} jobs need FIT scores\n")
    print("="*70)
    
    processed = 0
    errors = 0
    writes_this_minute = 0
    minute_start = time.time()
    
    for idx, job in enumerate(jobs_without_fit, 1):
        print(f"\n[{idx}/{len(jobs_without_fit)}]  @")
        print(f"   Row: {job['_row']}")
        
        # Check if we need to wait (rate limit protection)
        elapsed = time.time() - minute_start
        if writes_this_minute >= 55 and elapsed < 60:
            wait_time = int(60 - elapsed + 5)
            print(f"\n⏸️  Rate limit protection: waiting {wait_time}s...")
            time.sleep(wait_time)
            writes_this_minute = 0
            minute_start = time.time()
        
        # Reset counter after 1 minute
        if elapsed >= 60:
            writes_this_minute = 0
            minute_start = time.time()
        
        print(f"   🤖 Analyzing...")
        
        try:
            result = analyzer.analyze_job(job)
            fit = result.get('fit_score', 5)
            rec = result.get('recomendacion', '')
            print(f"   FIT: {fit}/10  [{rec}]")
            if result.get('tienes'):
                print(f"   Tienes: {result['tienes'][:80]}")
            if result.get('faltan'):
                print(f"   Faltan: {result['faltan'][:80]}")

            print(f"   Guardando...")

            updates = {
                'FitScore':  fit,
                'Why':       result.get('why', ''),
                'Seniority': result.get('seniority', ''),
                'Tienes':    result.get('tienes', ''),
                'Faltan':    result.get('faltan', ''),
            }

            sheet_manager.update_job(job['_row'], updates, 'linkedin')
            writes_this_minute += 1

            # Colorear la fila segun FIT (semaforo)
            sheet_manager.color_row_by_fit(job['_row'], fit, 'linkedin')

            print(f"   OK — color aplicado")
            processed += 1

            time.sleep(0.5)

        except Exception as e:
            print(f"   Error: {e}")
            errors += 1

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Procesados: {processed}")
    print(f"Errores:    {errors}")
    print("="*70)
    print("\nFIT scores calculados con gap analysis y semaforo de colores.")
    print(f"\nSheet: https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=0")

if __name__ == "__main__":
    main()
