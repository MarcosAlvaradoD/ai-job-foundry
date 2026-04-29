#!/usr/bin/env python3
"""
Deduplicar Sheet de LinkedIn
============================
El Sheet tiene filas duplicadas del mismo job — mismo LinkedIn Job ID aparece como:
  - /jobs/view/123456
  - /jobs/view/123456/        (con trailing slash)
  - /comm/jobs/view/123456    (variante /comm/)

Este script:
1. Identifica duplicados por Job ID
2. Mantiene la fila con más datos (company/role llenos, FIT score alto, etc.)
3. Marca los duplicados como "Skip - Duplicate" en la columna Status
4. O los elimina directamente (con --delete)

Uso:
  py scripts/maintenance/deduplicate_linkedin_sheet.py             # preview
  py scripts/maintenance/deduplicate_linkedin_sheet.py --apply     # marca Skip
  py scripts/maintenance/deduplicate_linkedin_sheet.py --delete    # elimina filas
"""
import sys
import re
import os
import argparse
import time
from pathlib import Path
from collections import defaultdict

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dotenv import load_dotenv
import gspread
from google.oauth2.credentials import Credentials

load_dotenv()

SHEET_ID   = os.getenv('GOOGLE_SHEETS_ID')
TOKEN_PATH = Path(__file__).parent.parent.parent / 'data' / 'credentials' / 'token.json'


def get_sheet(tab: str = 'LinkedIn'):
    creds = Credentials.from_authorized_user_file(
        str(TOKEN_PATH), ['https://www.googleapis.com/auth/spreadsheets']
    )
    return gspread.authorize(creds).open_by_key(SHEET_ID).worksheet(tab)


def extract_job_id(url: str) -> str | None:
    m = re.search(r'/jobs/(?:view|comm/jobs/view)/(\d+)', url)
    return m.group(1) if m else None


def row_quality_score(row: list, col: dict) -> int:
    """Score row quality — higher = more complete data, keep this one"""
    score = 0
    company = row[col['company']] if len(row) > col['company'] else ''
    role    = row[col['role']]    if len(row) > col['role']    else ''
    fit     = row[col['fit']]     if len(row) > col['fit']     else ''
    status  = row[col['status']]  if len(row) > col['status']  else ''
    url     = row[col['url']]     if len(row) > col['url']     else ''

    # Real company name
    if company and 'unknown' not in company.lower():
        score += 10
    # Real role name
    if role and 'pending' not in role.lower():
        score += 10
    # Has FIT score
    if fit and fit not in ('Unknown', ''):
        try:
            score += int(float(fit.split('/')[0]))
        except Exception:
            pass
    # Applied = keep for sure
    if 'applied' in status.lower():
        score += 50
    # Direct job URL (no trailing slash, no /comm/)
    if url and '/jobs/view/' in url and not url.endswith('/') and '/comm/' not in url:
        score += 2
    # Has notes
    notes_col = col.get('notes', -1)
    if notes_col >= 0 and len(row) > notes_col and row[notes_col]:
        score += 3

    return score


def main():
    parser = argparse.ArgumentParser(description='Deduplicar LinkedIn Sheet')
    parser.add_argument('--dry-run', action='store_true', help='Solo preview, no eliminar')
    parser.add_argument('--apply',   action='store_true', help='Marcar duplicados como Skip (no recomendado)')
    parser.add_argument('--delete',  action='store_true', help='Eliminar filas duplicadas (default)')
    parser.add_argument('--tab',     default='LinkedIn',  help='Sheet tab (default: LinkedIn)')
    args = parser.parse_args()

    # Default behavior is DELETE (not dry-run, not just marking)
    if not args.dry_run and not args.apply:
        args.delete = True

    dry_run = args.dry_run

    print("=" * 70)
    print("LinkedIn Sheet Deduplicator")
    mode = "DRY-RUN (preview)" if dry_run else ("MARK SKIP" if args.apply else "DELETE ROWS")
    print(f"Mode: {mode}")
    print("=" * 70)

    ws = get_sheet(args.tab)
    all_vals = ws.get_all_values()
    headers  = all_vals[0]

    col = {
        'company': next((i for i, h in enumerate(headers) if 'company' in h.lower()), 1),
        'role':    next((i for i, h in enumerate(headers) if h.lower() == 'role'), 2),
        'url':     next((i for i, h in enumerate(headers) if 'applyurl' in h.lower()), 5),
        'status':  next((i for i, h in enumerate(headers) if 'status' in h.lower()), 12),
        'fit':     next((i for i, h in enumerate(headers) if 'fitscore' in h.lower()), 17),
        'notes':   next((i for i, h in enumerate(headers) if 'notes' in h.lower()), -1),
    }

    # Group rows by LinkedIn Job ID
    id_to_rows: dict[str, list] = defaultdict(list)  # job_id -> [(sheet_row, row_data), ...]

    for sheet_row, row in enumerate(all_vals[1:], start=2):
        url = row[col['url']] if len(row) > col['url'] else ''
        job_id = extract_job_id(url)
        if job_id:
            id_to_rows[job_id].append((sheet_row, row))
        # Also track rows without job ID (no action needed, just count)

    # Find duplicates
    duplicates: list[tuple[str, list]] = [(jid, rows) for jid, rows in id_to_rows.items() if len(rows) > 1]

    print(f"\n[SCAN] Total rows: {len(all_vals)-1}")
    print(f"[SCAN] Unique job IDs: {len(id_to_rows)}")
    print(f"[SCAN] Duplicate groups: {len(duplicates)}")
    print(f"[SCAN] Extra rows (to remove): {sum(len(rows)-1 for _, rows in duplicates)}")

    if not duplicates:
        print("\n[OK] No duplicates found!")
        return

    # Decide which rows to keep/remove
    rows_to_skip   = []   # (sheet_row, company, role) to mark Skip
    rows_to_delete = []   # sheet_rows to delete (sorted descending for safe delete)

    for job_id, rows in duplicates:
        # Score each row — keep the best one
        scored = sorted(rows, key=lambda x: row_quality_score(x[1], col), reverse=True)
        keep_row, keep_data = scored[0]
        company = keep_data[col['company']] if len(keep_data) > col['company'] else '?'
        role    = keep_data[col['role']]    if len(keep_data) > col['role']    else '?'

        print(f"\n  Job {job_id}: {len(rows)} copies — KEEP row {keep_row} ({company} | {role})")
        for sheet_row, row_data in scored[1:]:
            r_company = row_data[col['company']] if len(row_data) > col['company'] else '?'
            r_role    = row_data[col['role']]    if len(row_data) > col['role']    else '?'
            r_url     = row_data[col['url']]     if len(row_data) > col['url']     else '?'
            print(f"    REMOVE row {sheet_row}: {r_company} | {r_role}")
            print(f"      URL: {r_url[:70]}")
            rows_to_skip.append((sheet_row, r_company, r_role))
            rows_to_delete.append(sheet_row)

    # Also find rows already marked "Skip - Duplicate" from previous runs
    already_marked = []
    for sheet_row, row in enumerate(all_vals[1:], start=2):
        status = row[col['status']] if len(row) > col['status'] else ''
        if status == 'Skip - Duplicate' and sheet_row not in rows_to_delete:
            already_marked.append(sheet_row)

    if already_marked:
        print(f"\n[FOUND] {len(already_marked)} rows already marked 'Skip - Duplicate' — adding to delete list")
        rows_to_delete.extend(already_marked)

    print(f"\n[PLAN] {len(rows_to_delete)} rows to remove total")

    if dry_run:
        print("\n[DRY-RUN] No changes made.")
        print("[TIP] Run without --dry-run to delete (default), or --apply to mark as Skip")
        return

    if args.apply:
        # Mark duplicate rows as Skip in Status column
        status_col_idx = col['status'] + 1  # gspread is 1-indexed
        updates = []
        for sheet_row, _, _ in rows_to_skip:
            updates.append(gspread.Cell(sheet_row, status_col_idx, 'Skip - Duplicate'))
        if updates:
            ws.update_cells(updates)
            print(f"\n[OK] Marked {len(updates)} rows as 'Skip - Duplicate'")

    elif args.delete:
        # Batch delete using Sheets batchUpdate API — single request, no rate limit issues
        rows_to_delete_sorted = sorted(set(rows_to_delete), reverse=True)

        # Get the numeric sheet ID (sheetId) for batchUpdate
        spreadsheet = ws.spreadsheet
        sheet_id_num = ws.id  # gspread worksheet.id gives the numeric sheetId

        # Build delete requests: each deletes one row range
        # Must be sorted descending so row indices remain valid as we delete from bottom up
        delete_requests = []
        for sheet_row in rows_to_delete_sorted:
            delete_requests.append({
                "deleteDimension": {
                    "range": {
                        "sheetId":    sheet_id_num,
                        "dimension":  "ROWS",
                        "startIndex": sheet_row - 1,  # 0-indexed
                        "endIndex":   sheet_row,      # exclusive
                    }
                }
            })

        # Send in batches of 100 (API max is 1000 but 100 is safe)
        batch_size = 100
        deleted = 0
        for i in range(0, len(delete_requests), batch_size):
            batch = delete_requests[i:i + batch_size]
            spreadsheet.batch_update({"requests": batch})
            deleted += len(batch)
            print(f"  Deleted {deleted}/{len(delete_requests)} rows...")
            if i + batch_size < len(delete_requests):
                time.sleep(2)

        print(f"\n[OK] Deleted {deleted} duplicate rows from Sheet")

    print("\n[DONE] Deduplication complete!")
    print(f"[TIP] Run enrich_unknown_jobs.py to fill company/role for remaining Unknown rows")


if __name__ == '__main__':
    main()
