"""Orphaned file cleanup job.

Finds and deletes files that exist on disk but have no corresponding
database record. Runs as a periodic task.

Implemented by Copilot
"""

from pathlib import Path
import logging

from sqlalchemy import select
from storage.database.connect import AsyncSessionLocal
from storage.database.models import Asset
from services.ingestion.storage import RAW_DIR

# set up logs
logger = logging.getLogger(__name__)


async def cleanup_orphaned_files() -> dict:
    """Find and delete orphaned files in storage.
    Args:
        None
    Returns:
        dict with keys -> dict {
            - total_files: set -> Total files found on disk
            - db_files: set -> files found in database
            - orphans_deleted: int -> Number of orphaned files deleted
            - errors: arr -> List of errors encountered }
    """
    errors = []
    orphans_deleted = 0

    try:
        # Get all files from storage
        files_on_disk = set()
        for file_path in RAW_DIR.rglob("*"):
            if file_path.is_file():
                files_on_disk.add(str(file_path))

        logger.info(f"Found {len(files_on_disk)} files on disk")

        # Get all files from database
        async with AsyncSessionLocal() as db:
            statement = select(Asset.stored_path)
            result = await db.execute(statement)
            files_in_db = {row[0] for row in result.scalars()}

        logger.info(f"Found {len(files_in_db)} files in database")

        # Find orphans
        orphans = files_on_disk - files_in_db

        if not orphans:
            logger.info("No orphaned files found")
            return {
                "total_files": len(files_on_disk),
                "db_files": len(files_in_db),
                "orphans_deleted": 0,
                "errors": [],
            }

        logger.warning(f"Found {len(orphans)} orphaned files")

        # Delete orphans
        for orphan_path in orphans:
            try:
                path = Path(orphan_path)
                path.unlink()
                orphans_deleted += 1
                logger.info(f"Deleted orphaned file: {orphan_path}")
            except Exception as e:
                error_msg = f"Failed to delete orphan {orphan_path}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        logger.info(f"Cleanup complete. Deleted {orphans_deleted} orphaned files")

        return {
            "total_files": len(files_on_disk),
            "db_files": len(files_in_db),
            "orphans_deleted": orphans_deleted,
            "errors": errors,
        }

    except Exception as e:
        error_msg = f"Orphan cleanup job failed: {e}"
        logger.error(error_msg)
        return {
            "total_files": 0,
            "db_files": 0,
            "orphans_deleted": 0,
            "errors": [error_msg],
        }
