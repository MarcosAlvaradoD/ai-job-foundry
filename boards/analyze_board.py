#!/usr/bin/env python3
"""
AI JOB FOUNDRY - JOB BOARD ANALYZER
Analiza boards de empleo completos (ej: RH-IT Home)

Uso:
    py boards\analyze_board.py --url "https://vacantes.rh-itchome.com/"
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import argparse
import re
from core.enrichment.ai_analyzer import AIAnalyzer
from dotenv import load_dotenv

load_dotenv()

class JobBoardAnalyzer:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.ai_analyzer = AIAnalyzer()
        self.job_links = []
        self.results = []

    async def find_all_job_links(self) -> list:
        """Encuentra TODOS los enlaces a vacantes en el board"""
        print(f"\n🔍 Analizando board: {self.base_url}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(self.base_url, wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(2)
                
                all_links = await page.query_selector_all('a[href]')
                job_links = set()
                
                for link in all_links:
                    try:
                        href = await link.get_attribute('href')
                        if not href:
                            continue
                        
                        if href.startswith('/'):
                            full_url = self.base_url.rstrip('/') + href
                        elif href.startswith('http'):
                            full_url = href
                        else:
                            continue
                        
                        job_patterns = [
                            r'/vacante/\d+', r'/job/\d+', r'/empleo/\d+',
                            r'/position/\d+', r'/posting/\d+', r'/opening/\d+'
                        ]
                        
                        if any(re.search(pattern, full_url) for pattern in job_patterns):
                            job_links.add(full_url)
                    except Exception:
                        continue
                
                await browser.close()
                job_links = sorted(list(job_links))
                print(f"  ✅ Encontrados {len(job_links)} enlaces a vacantes")
                return job_links
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                await browser.close()
                return []

    async def extract_job_content(self, url: str) -> dict:
        """Extrae contenido de UNA vacante"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(2)
                
                full_text = await page.inner_text('body')
                
                title = "Unknown"
                title_selectors = ['h1', '.job-title', '[class*="title"]']
                for selector in title_selectors:
                    try:
                        title_elem = await page.query_selector(selector)
                        if title_elem:
                            title = await title_elem.inner_text()
                            title = title.strip()
                            if title and len(title) > 3:
                                break
                    except Exception:
                        continue
                
                company = "Unknown"
                company_selectors = ['.company', '[class*="empresa"]']
                for selector in company_selectors:
                    try:
                        company_elem = await page.query_selector(selector)
                        if company_elem:
                            company = await company_elem.inner_text()
                            company = company.strip()
                            if company and len(company) > 2:
                                break
                    except Exception:
                        continue
                
                await browser.close()
                return {'url': url, 'title': title, 'company': company, 'full_text': full_text[:5000]}
            except Exception as e:
                await browser.close()
                return None

    def analyze_with_ai(self, job_content: dict) -> dict:
        """Analiza con IA para calcular FIT score"""
        job_data = {
            'Role': job_content.get('title', 'Unknown'),
            'Company': job_content.get('company', 'Unknown'),
            'ApplyURL': job_content.get('url', ''),
            'full_description': job_content.get('full_text', '')
        }
        
        result = self.ai_analyzer.analyze_job(job_data)
        
        return {
            'url': job_content.get('url', ''),
            'title': job_content.get('title', 'Unknown'),
            'company': job_content.get('company', 'Unknown'),
            'fit_score': result.get('fit_score', 0),
            'why': result.get('why', ''),
            'seniority': result.get('seniority', 'Unknown')
        }
    
    async def analyze_all_jobs(self):
        """Analiza TODAS las vacantes del board"""
        self.job_links = await self.find_all_job_links()
        
        if not self.job_links:
            print("\n⚠️  No se encontraron vacantes")
            return
        
        print(f"\n🤖 Analizando {len(self.job_links)} vacantes con IA...")
        
        for i, url in enumerate(self.job_links, 1):
            print(f"\n[{i}/{len(self.job_links)}] Procesando: {url}")
            content = await self.extract_job_content(url)
            if not content:
                print(f"  ❌ Error extrayendo contenido")
                continue
            
            print(f"  🤖 Analizando con IA...")
            analysis = self.analyze_with_ai(content)
            print(f"  ✅ FIT: {analysis['fit_score']}/10 - {analysis['title']}")
            self.results.append(analysis)
            await asyncio.sleep(3)

    def save_results_to_txt(self, output_file: str = 'board_analysis.txt'):
        """Guarda resultados en TXT"""
        if not self.results:
            print("\n⚠️  No hay resultados para guardar")
            return
        
        sorted_results = sorted(self.results, key=lambda x: x['fit_score'], reverse=True)
        output_path = Path(__file__).parent / output_file
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("AI JOB FOUNDRY - BOARD ANALYSIS RESULTS\n")
            f.write(f"Board: {self.base_url}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"Total Jobs: {len(self.results)}\n")
            f.write("="*70 + "\n\n")
            
            for i, job in enumerate(sorted_results, 1):
                f.write(f"[{i}] FIT: {job['fit_score']}/10 | {job['title']}\n")
                f.write(f"    Company: {job['company']}\n")
                f.write(f"    URL: {job['url']}\n")
                f.write(f"    WHY: {job['why']}\n")
                f.write("-"*70 + "\n\n")
        
        print(f"\n💾 Resultados guardados en: {output_path}")
        print(f"   Total vacantes analizadas: {len(self.results)}")
        
        high_fit = [j for j in sorted_results if j['fit_score'] >= 7]
        medium_fit = [j for j in sorted_results if 5 <= j['fit_score'] < 7]
        low_fit = [j for j in sorted_results if j['fit_score'] < 5]
        
        print(f"\n📊 RESUMEN:")
        print(f"   🟢 FIT Alto (7+):  {len(high_fit)} vacantes")
        print(f"   🟡 FIT Medio (5-6): {len(medium_fit)} vacantes")
        print(f"   🔴 FIT Bajo (<5):   {len(low_fit)} vacantes")

async def main():
    parser = argparse.ArgumentParser(description='Analizar board de empleos completo')
    parser.add_argument('--url', required=True, help='URL principal del board')
    parser.add_argument('--output', default='board_analysis.txt', help='Archivo de salida')
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🎯 AI JOB FOUNDRY - JOB BOARD ANALYZER")
    print("="*70)
    
    analyzer = JobBoardAnalyzer(args.url)
    await analyzer.analyze_all_jobs()
    analyzer.save_results_to_txt(args.output)
    
    print("\n" + "="*70)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())
