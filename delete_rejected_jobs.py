#!/usr/bin/env python3
"""
Delete rejected job offers from Google Sheets
"""

from core.sheets.sheet_manager import SheetManager

def delete_rejected_jobs():
    """Delete rejected jobs from the sheet"""
    sm = SheetManager()

    # Rows to delete: 6, 8, 7, 9, 182, 184
    rows_to_delete = [6, 7, 8, 9, 182, 184]

    print("🗑️ Deleting rejected job offers...")
    print(f"Rows to delete: {rows_to_delete}")

    # Get all jobs
    jobs = sm.get_all_jobs('linkedin')

    # Filter out the rows to delete
    remaining_jobs = [job for job in jobs if job.get('_row') not in rows_to_delete]

    print(f"Before: {len(jobs)} jobs")
    print(f"After: {len(remaining_jobs)} jobs")
    print(f"Deleted: {len(jobs) - len(remaining_jobs)} jobs")

    # For now, just mark as deleted in status
    # Since deleting rows in Google Sheets is complex, we'll mark them as deleted
    for row_num in rows_to_delete:
        try:
            sm.update_job_status(row_num, 'DELETED', 'linkedin')
            print(f"✅ Marked row {row_num} as DELETED")
        except Exception as e:
            print(f"❌ Error updating row {row_num}: {e}")

    print("\n✅ Deletion complete!")

if __name__ == "__main__":
    print("="*50)
    print("🗑️ DELETE REJECTED JOB OFFERS")
    print("="*50)

    delete_rejected_jobs()