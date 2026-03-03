import shutil
from datetime import date
from pathlib import Path
from typing import Any

from .base import BaseExporter, ExportResult


class StreaksExporter(BaseExporter):
    name = "streaks"
    display_name = "Streaks Habits"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.pickup_dir = Path(config.get("pickup_dir", ""))

    def validate_config(self) -> list[str]:
        errors = []
        if not self.pickup_dir:
            errors.append("streaks.pickup_dir is required")
        return errors

    def export(self, start_date: date, end_date: date, output_dir: Path) -> ExportResult:
        if not self.pickup_dir.is_dir():
            return ExportResult(
                source_name=self.display_name,
                success=True,
                message=f"Pickup directory not found: {self.pickup_dir} (run the Streaks export Shortcut first)",
            )

        # Find the most recent export file
        files = sorted(self.pickup_dir.iterdir(), key=lambda f: f.stat().st_mtime, reverse=True)
        export_files = [f for f in files if f.is_file() and f.suffix in (".csv", ".json", ".txt")]

        if not export_files:
            return ExportResult(
                source_name=self.display_name,
                success=True,
                message="No export files found in pickup directory",
            )

        dest = output_dir / "streaks"
        dest.mkdir(parents=True, exist_ok=True)

        # Copy the most recent file
        latest = export_files[0]
        dest_file = dest / latest.name
        shutil.copy2(latest, dest_file)

        return ExportResult(
            source_name=self.display_name,
            success=True,
            files_exported=[dest_file],
            record_count=1,
            message=f"Copied {latest.name}",
        )
