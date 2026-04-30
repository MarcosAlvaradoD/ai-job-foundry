#!/usr/bin/env python3
"""
CI Runner — Job Cleanup para GitHub Actions
============================================
Elimina filas antiguas de Google Sheets según reglas de retención:
  - New:       > 30 días → eliminar
  - Reviewed:  > 45 días → eliminar
  - Applied:   > 90 días → eliminar
  - Rejected:  siempre  → eliminar (día 1)
  - Interview: > 90 días → eliminar

Uso (automático vía workflow):
  python scripts/ci/run_cleanup_ci.py
"""
import sys
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

# ── Logging a archivo + stdout ─────────────────────────────────────────────────
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
log_file = LOG_DIR / f"cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

# PROJECT_ROOT debe apuntar al workspace
os.environ.setdefault("PROJECT_ROOT", str(ROOT))

# ── Reglas de retención ────────────────────────────────────────────────────────
# status → max días permitidos (None = eliminar siempre)
RETENTION_DAYS: dict[str, int | None] = {
    "new":       30,
    "reviewed":  45,
    "applied":   90,
    "rejected":  None,   # siempre eliminar
    "interview": 90,
}

TABS = ["linkedin", "indeed", "computrabajo"]
DATE_FORMAT = "%Y-%m-%d"


def should_delete(status: str, date_found_str: str, today: datetime) -> bool:
    """Returns True if the row should be deleted based on retention rules."""
    if not date_found_str:
        return False  # no date → skip

    try:
        date_found = datetime.strptime(date_found_str.strip(), DATE_FORMAT)
    except ValueError:
        log.warning(f"Could not parse DateFound: '{date_found_str}' — skipping row")
        return False

    status_lower = status.strip().lower() if status else ""
    max_days = RETENTION_DAYS.get(status_lower)

    if max_days is None:
        # "rejected" or unrecognized status with explicit None → always delete
        if status_lower in RETENTION_DAYS:
            return True
        # Unrecognized status (not in dict) → skip
        return False

    age_days = (today - date_found).days
    return age_days > max_days


def get_sheet_id(sheet_manager, tab_key: str) -> int | None:
    """Get the numeric sheetId for a tab key."""
    tab_name = sheet_manager.tabs.get(tab_key)
    if not tab_name:
        return None
    try:
        spreadsheet = sheet_manager.service.spreadsheets().get(
            spreadsheetId=sheet_manager.spreadsheet_id
        ).execute()
        for sheet in spreadsheet.get("sheets", []):
            props = sheet.get("sheetProperties", {})
            if props.get("title") == tab_name:
                return props.get("sheetId")
    except Exception as e:
        log.error(f"Error getting sheetId for '{tab_key}': {e}")
    return None


def delete_rows_batch(sheet_manager, sheet_id: int, row_indices: list[int]):
    """
    Delete rows by 1-based row index (row 1 = headers, data starts at row 2).
    Deletes from bottom to top so indices don't shift during deletion.
    Uses batchUpdate with deleteDimension requests.
    """
    if not row_indices:
        return 0

    # Sort descending so we delete from bottom to top
    sorted_indices = sorted(row_indices, reverse=True)

    requests = []
    for row_1based in sorted_indices:
        # API uses 0-based index for startIndex
        start_index = row_1based - 1  # convert to 0-based
        requests.append({
            "deleteDimension": {
                "range": {
                    "sheetId":    sheet_id,
                    "dimension":  "ROWS",
                    "startIndex": start_index,
                    "endIndex":   start_index + 1,
                }
            }
        })

    try:
        sheet_manager.service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_manager.spreadsheet_id,
            body={"requests": requests},
        ).execute()
        return len(row_indices)
    except Exception as e:
        log.error(f"batchUpdate error: {e}")
        return 0


def cleanup_tab(sheet_manager, tab_key: str, today: datetime) -> int:
    """Process one tab: find rows to delete, delete them, return count."""
    log.info(f"--- Processing tab: {tab_key} ---")

    # Read all rows
    try:
        rows = sheet_manager.get_all_jobs(tab=tab_key)
    except Exception as e:
        log.warning(f"  Could not read tab '{tab_key}': {e} — skipping")
        return 0

    if not rows:
        log.info(f"  Tab '{tab_key}' is empty — nothing to clean")
        return 0

    log.info(f"  Total rows: {len(rows)}")

    # Find row indices to delete
    # get_all_jobs returns dicts; row 1 = headers, data rows start at index 2
    to_delete: list[int] = []
    for idx, row in enumerate(rows):
        # Row number in sheet: header=1, first data row=2, so sheet_row = idx + 2
        sheet_row = idx + 2
        status     = row.get("Status", "")
        date_found = row.get("DateFound", "")

        if should_delete(status, date_found, today):
            to_delete.append(sheet_row)
            log.debug(f"  Mark for delete: row {sheet_row} | Status={status} | DateFound={date_found}")

    log.info(f"  Rows to delete: {len(to_delete)}")

    if not to_delete:
        return 0

    # Get numeric sheetId
    sheet_id = get_sheet_id(sheet_manager, tab_key)
    if sheet_id is None:
        log.error(f"  Could not get sheetId for '{tab_key}' — skipping deletion")
        return 0

    deleted = delete_rows_batch(sheet_manager, sheet_id, to_delete)
    log.info(f"  Deleted: {deleted} rows from '{tab_key}'")
    return deleted


def main():
    log.info("=" * 60)
    log.info("Job Cleanup CI — Google Sheets")
    log.info(f"Root    : {ROOT}")
    log.info(f"Log     : {log_file}")
    log.info(f"Date    : {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    log.info("=" * 60)

    # Verify credentials
    creds = [
        ROOT / "data" / "credentials" / "credentials.json",
        ROOT / "data" / "credentials" / "token.json",
    ]
    missing = [str(c) for c in creds if not c.exists()]
    if missing:
        log.error(f"Missing credentials: {missing}")
        log.error("Check that GitHub Secrets are configured correctly.")
        sys.exit(1)

    log.info("Credentials: OK")

    try:
        from core.sheets.sheet_manager import SheetManager
        sheet_manager = SheetManager()
    except ImportError as e:
        log.error(f"Import error: {e}")
        sys.exit(1)
    except Exception as e:
        log.error(f"SheetManager init error: {e}", exc_info=True)
        sys.exit(1)

    today = datetime.now()
    total_deleted = 0

    for tab_key in TABS:
        try:
            deleted = cleanup_tab(sheet_manager, tab_key, today)
            total_deleted += deleted
        except Exception as e:
            log.error(f"Error processing tab '{tab_key}': {e}", exc_info=True)

    log.info("=" * 60)
    log.info(f"TOTAL ELIMINADAS: {total_deleted} filas")
    log.info("=" * 60)

    sys.exit(0)


if __name__ == "__main__":
    main()
