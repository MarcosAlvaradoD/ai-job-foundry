#!/usr/bin/env python3
"""
GOOGLE SHEETS ANALYZER
Analiza qué columnas se usan, cuáles no, y qué datos están vacíos

Genera reporte completo del estado del Google Sheet
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.sheets.sheet_manager import SheetManager
from collections import Counter
from datetime import datetime

def analyze_column_usage(jobs: list) -> dict:
    """Analyze which columns are used and which are empty"""
    
    if not jobs:
        return {}
    
    # Get all possible columns
    all_columns = set()
    for job in jobs:
        all_columns.update(job.keys())
    
    # Analyze each column
    column_stats = {}
    for col in sorted(all_columns):
        non_empty = sum(1 for job in jobs if job.get(col) and str(job.get(col)).strip())
        empty = len(jobs) - non_empty
        usage_pct = (non_empty / len(jobs)) * 100 if jobs else 0
        
        # Get sample values (first 3 non-empty)
        samples = []
        for job in jobs:
            val = job.get(col)
            if val and str(val).strip() and len(samples) < 3:
                samples.append(str(val)[:50])
        
        column_stats[col] = {
            'non_empty': non_empty,
            'empty': empty,
            'usage_pct': usage_pct,
            'samples': samples
        }
    
    return column_stats

def analyze_status_distribution(jobs: list) -> dict:
    """Analyze distribution of job statuses"""
    statuses = [job.get('Status', 'Unknown') for job in jobs]
    return dict(Counter(statuses))

def analyze_fit_scores(jobs: list) -> dict:
    """Analyze FIT score distribution"""
    scores = []
    for job in jobs:
        fit = job.get('FitScore', '0')
        try:
            # Handle "8/10" format
            if '/' in str(fit):
                fit = int(str(fit).split('/')[0])
            else:
                fit = int(fit) if fit else 0
            scores.append(fit)
        except Exception:
            scores.append(0)
    
    score_dist = dict(Counter(scores))
    
    return {
        'distribution': score_dist,
        'avg': sum(scores) / len(scores) if scores else 0,
        'max': max(scores) if scores else 0,
        'min': min(scores) if scores else 0,
        'high_fit': sum(1 for s in scores if s >= 7),
        'medium_fit': sum(1 for s in scores if 4 <= s < 7),
        'low_fit': sum(1 for s in scores if 0 < s < 4),
        'unscored': sum(1 for s in scores if s == 0)
    }

def analyze_sources(jobs: list) -> dict:
    """Analyze job sources"""
    sources = [job.get('Source', 'Unknown') for job in jobs]
    return dict(Counter(sources))

def analyze_dates(jobs: list) -> dict:
    """Analyze creation dates"""
    from datetime import datetime, timedelta
    
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    last_week = 0
    last_month = 0
    older = 0
    no_date = 0
    
    for job in jobs:
        created = job.get('CreatedAt', '')
        if not created:
            no_date += 1
            continue
        
        try:
            created_date = datetime.fromisoformat(created)
            if created_date >= week_ago:
                last_week += 1
            elif created_date >= month_ago:
                last_month += 1
            else:
                older += 1
        except Exception:
            no_date += 1
    
    return {
        'last_week': last_week,
        'last_month': last_month,
        'older': older,
        'no_date': no_date
    }

def main():
    print("\n" + "="*80)
    print("📊 GOOGLE SHEETS ANALYZER")
    print("="*80)
    print("Analizando estructura y datos del Google Sheet...")
    print("="*80 + "\n")
    
    try:
        sm = SheetManager()
        jobs = sm.get_all_jobs()
        
        if not jobs:
            print("❌ No se encontraron jobs en el sheet")
            return
        
        print(f"✅ {len(jobs)} jobs encontrados\n")
        
        # 1. Column Usage Analysis
        print("="*80)
        print("📋 ANÁLISIS DE COLUMNAS")
        print("="*80)
        column_stats = analyze_column_usage(jobs)
        
        # Sort by usage
        sorted_cols = sorted(column_stats.items(), key=lambda x: x[1]['usage_pct'], reverse=True)
        
        print("\n🟢 COLUMNAS MÁS USADAS (>80%):\n")
        for col, stats in sorted_cols:
            if stats['usage_pct'] > 80:
                print(f"  {col:20s}: {stats['non_empty']:4d}/{len(jobs)} ({stats['usage_pct']:5.1f}%)")
                if stats['samples']:
                    print(f"      Ejemplos: {stats['samples'][0]}")
        
        print("\n🟡 COLUMNAS PARCIALMENTE USADAS (20-80%):\n")
        for col, stats in sorted_cols:
            if 20 < stats['usage_pct'] <= 80:
                print(f"  {col:20s}: {stats['non_empty']:4d}/{len(jobs)} ({stats['usage_pct']:5.1f}%)")
        
        print("\n🔴 COLUMNAS POCO USADAS (<20%):\n")
        for col, stats in sorted_cols:
            if stats['usage_pct'] <= 20:
                print(f"  {col:20s}: {stats['non_empty']:4d}/{len(jobs)} ({stats['usage_pct']:5.1f}%)")
        
        # 2. Status Distribution
        print("\n" + "="*80)
        print("📊 DISTRIBUCIÓN DE STATUS")
        print("="*80 + "\n")
        status_dist = analyze_status_distribution(jobs)
        for status, count in sorted(status_dist.items(), key=lambda x: x[1], reverse=True):
            pct = (count / len(jobs)) * 100
            bar = "█" * int(pct / 2)
            print(f"  {status:20s}: {count:4d} ({pct:5.1f}%) {bar}")
        
        # 3. FIT Score Analysis
        print("\n" + "="*80)
        print("🎯 ANÁLISIS DE FIT SCORES")
        print("="*80 + "\n")
        fit_stats = analyze_fit_scores(jobs)
        print(f"  Promedio:      {fit_stats['avg']:.2f}/10")
        print(f"  Máximo:        {fit_stats['max']}/10")
        print(f"  Mínimo:        {fit_stats['min']}/10")
        print(f"\n  High Fit (7+):   {fit_stats['high_fit']} ({fit_stats['high_fit']/len(jobs)*100:.1f}%)")
        print(f"  Medium Fit (4-6): {fit_stats['medium_fit']} ({fit_stats['medium_fit']/len(jobs)*100:.1f}%)")
        print(f"  Low Fit (1-3):    {fit_stats['low_fit']} ({fit_stats['low_fit']/len(jobs)*100:.1f}%)")
        print(f"  Sin calificar:    {fit_stats['unscored']} ({fit_stats['unscored']/len(jobs)*100:.1f}%)")
        
        print("\n  Distribución por score:")
        for score in range(10, -1, -1):
            count = fit_stats['distribution'].get(score, 0)
            if count > 0:
                bar = "█" * int((count / len(jobs)) * 50)
                print(f"    {score:2d}/10: {count:4d} {bar}")
        
        # 4. Sources Analysis
        print("\n" + "="*80)
        print("📡 ANÁLISIS DE FUENTES")
        print("="*80 + "\n")
        sources = analyze_sources(jobs)
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            pct = (count / len(jobs)) * 100
            print(f"  {source:20s}: {count:4d} ({pct:5.1f}%)")
        
        # 5. Dates Analysis
        print("\n" + "="*80)
        print("📅 ANÁLISIS TEMPORAL")
        print("="*80 + "\n")
        dates = analyze_dates(jobs)
        print(f"  Última semana:    {dates['last_week']}")
        print(f"  Último mes:       {dates['last_month']}")
        print(f"  Más antiguos:     {dates['older']}")
        print(f"  Sin fecha:        {dates['no_date']}")
        
        # 6. Recommendations
        print("\n" + "="*80)
        print("💡 RECOMENDACIONES")
        print("="*80 + "\n")
        
        # Check for unused columns
        unused_cols = [col for col, stats in column_stats.items() if stats['usage_pct'] < 5]
        if unused_cols:
            print("  🗑️  Columnas casi sin usar (considerar eliminar):")
            for col in unused_cols:
                print(f"     - {col}")
        
        # Check for missing FIT scores
        if fit_stats['unscored'] > 10:
            print(f"\n  ⚠️  {fit_stats['unscored']} jobs sin FIT score - ejecutar AI analyzer")
        
        # Check for old jobs
        if dates['older'] > 50:
            print(f"\n  🗑️  {dates['older']} jobs de hace más de 30 días - considerar archivar")
        
        # Check for missing URLs
        url_stats = column_stats.get('ApplyURL', {})
        if url_stats and url_stats['empty'] > 10:
            print(f"\n  ⚠️  {url_stats['empty']} jobs sin URL - revisar extractores")
        
        print("\n" + "="*80)
        print("✅ ANÁLISIS COMPLETO")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
