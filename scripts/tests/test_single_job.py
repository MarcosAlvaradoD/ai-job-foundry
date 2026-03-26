"""
Test single job analysis with new model (Llama-3-Groq-70B).

Purpose: Quick test to verify model change worked correctly.
Location: scripts/tests/test_single_job.py

Usage:
    py scripts\\tests\\test_single_job.py
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.enrichment.ai_analyzer import AIAnalyzer
from core.sheets.sheet_manager import SheetManager


def test_single_job():
    """Test AI analysis on a single job from Google Sheets."""
    
    print("\n" + "="*60)
    print("🧪 TEST: Single Job Analysis with New Model")
    print("="*60 + "\n")
    
    # Initialize components
    print("📊 Loading job from Google Sheets...")
    sheet_manager = SheetManager()
    
    # Get one job from Jobs tab (first non-Registry job)
    jobs_df = sheet_manager.read_sheet("Jobs")
    
    if jobs_df.empty:
        print("❌ ERROR: No jobs found in Google Sheets")
        return False
    
    # Filter out Registry entries and get first job
    actual_jobs = jobs_df[jobs_df['Company'] != 'Registry'].head(1)
    
    if actual_jobs.empty:
        print("❌ ERROR: No actual jobs found (only Registry entries)")
        return False
    
    job_row = actual_jobs.iloc[0]
    
    print(f"\n📋 Selected Job:")
    print(f"   Company: {job_row.get('Company', 'Unknown')}")
    print(f"   Role: {job_row.get('Role', 'Unknown')}")
    print(f"   Location: {job_row.get('Location', 'Unknown')}")
    print(f"   Current FIT Score: {job_row.get('FitScore', 'N/A')}")
    
    # Convert to dict
    job_data = job_row.to_dict()
    
    # Initialize AI Analyzer
    print("\n🤖 Initializing AI Analyzer...")
    analyzer = AIAnalyzer()
    
    # Load CV descriptor
    cv_path = project_root / "data" / "cv_descriptor.txt"
    if not cv_path.exists():
        print(f"❌ ERROR: CV descriptor not found at {cv_path}")
        return False
    
    with open(cv_path, 'r', encoding='utf-8') as f:
        cv_descriptor = f.read()
    
    print(f"✅ CV Descriptor loaded ({len(cv_descriptor)} chars)")
    
    # Analyze job
    print("\n🔬 Analyzing job with new model...")
    print("   (This may take 10-20 seconds with Llama-3-Groq-70B)")
    
    try:
        enriched = analyzer.analyze_job(job_data, cv_descriptor)
        
        print("\n" + "="*60)
        print("✅ ANALYSIS RESULTS:")
        print("="*60)
        
        print(f"\n🎯 FIT SCORE: {enriched.get('FitScore', 'N/A')}/10")
        print(f"\n📝 JUSTIFICATION:")
        print(f"   {enriched.get('Justification', 'N/A')}")
        
        print(f"\n💪 CANDIDATE STRENGTHS:")
        strengths = enriched.get('CandidateStrengths', [])
        if isinstance(strengths, list):
            for i, strength in enumerate(strengths, 1):
                print(f"   {i}. {strength}")
        else:
            print(f"   {strengths}")
        
        print(f"\n⚠️  MISSING REQUIREMENTS:")
        gaps = enriched.get('MissingRequirements', [])
        if isinstance(gaps, list):
            for i, gap in enumerate(gaps, 1):
                print(f"   {i}. {gap}")
        else:
            print(f"   {gaps}")
        
        print(f"\n🎯 RECOMMENDATION: {enriched.get('ApplyRecommendation', 'N/A')}")
        print(f"💰 SALARY MATCH: {enriched.get('SalaryMatch', 'N/A')}")
        print(f"🏠 REMOTE: {enriched.get('RemoteCompatibility', 'N/A')}")
        
        # Validation checks
        print("\n" + "="*60)
        print("🔍 VALIDATION CHECKS:")
        print("="*60 + "\n")
        
        checks = []
        
        # Check 1: FIT_SCORE is integer
        fit_score = enriched.get('FitScore')
        if isinstance(fit_score, int) and 0 <= fit_score <= 10:
            checks.append("✅ FIT_SCORE is valid integer (0-10)")
        else:
            checks.append(f"❌ FIT_SCORE invalid: {fit_score} (type: {type(fit_score)})")
        
        # Check 2: Justification exists and is reasonable length
        justification = enriched.get('Justification', '')
        if justification and len(justification) > 20:
            checks.append(f"✅ Justification exists ({len(justification)} chars)")
        else:
            checks.append(f"❌ Justification too short or missing")
        
        # Check 3: Strengths is list with items
        if isinstance(strengths, list) and len(strengths) > 0:
            checks.append(f"✅ Candidate strengths provided ({len(strengths)} items)")
        else:
            checks.append(f"❌ Candidate strengths missing or invalid")
        
        # Check 4: No obvious hallucinations (check if strengths mention CV keywords)
        cv_keywords = [
            "project manager", "product owner", "business analyst",
            "erp", "dynamics", "etl", "power bi", "scrum", "agile",
            "nefab", "tcs", "toyota", "medisist"
        ]
        
        hallucination_check = True
        if isinstance(strengths, list):
            for strength in strengths:
                strength_lower = strength.lower()
                # Check if strength contains ANY CV keyword
                has_keyword = any(keyword in strength_lower for keyword in cv_keywords)
                if not has_keyword and len(strength) > 20:
                    hallucination_check = False
                    checks.append(f"⚠️  Possible hallucination: '{strength}'")
        
        if hallucination_check:
            checks.append("✅ No obvious hallucinations detected")
        
        for check in checks:
            print(check)
        
        # Final verdict
        print("\n" + "="*60)
        all_passed = all("✅" in check for check in checks if not check.startswith("⚠️"))
        if all_passed:
            print("🎉 ALL CHECKS PASSED - Model working correctly!")
            return True
        else:
            print("⚠️  SOME CHECKS FAILED - Review configuration")
            return False
        
    except Exception as e:
        print(f"\n❌ ERROR during analysis:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_single_job()
    sys.exit(0 if success else 1)
