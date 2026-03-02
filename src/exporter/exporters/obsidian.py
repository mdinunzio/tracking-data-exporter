import re
import shutil
from datetime import date, datetime
from pathlib import Path
from typing import Any

from .base import BaseExporter, ExportResult

DATE_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})\.(md|txt)$")


class ObsidianExporter(BaseExporter):
    name = "obsidian"
    display_name = "Obsidian Daily Journals"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.vault_path = Path(config.get("vault_path", ""))

    def validate_config(self) -> list[str]:
        errors = []
        if not self.vault_path:
            errors.append("obsidian.vault_path is required")
        elif not self.vault_path.is_dir():
            errors.append(f"obsidian.vault_path does not exist: {self.vault_path}")
        return errors

    def export(self, start_date: date, end_date: date, output_dir: Path) -> ExportResult:
        dest = output_dir / "obsidian"
        dest.mkdir(parents=True, exist_ok=True)

        exported: list[Path] = []
        for entry in sorted(self.vault_path.iterdir()):
            if not entry.is_file():
                continue
            match = DATE_PATTERN.match(entry.name)
            if not match:
                continue
            file_date = datetime.strptime(match.group(1), "%Y-%m-%d").date()
            if start_date <= file_date <= end_date:
                dest_file = dest / entry.name
                shutil.copy2(entry, dest_file)
                exported.append(dest_file)

        if not exported:
            return ExportResult(
                source_name=self.display_name,
                success=True,
                message=f"No journal entries found for {start_date} to {end_date}",
            )

        return ExportResult(
            source_name=self.display_name,
            success=True,
            files_exported=exported,
            record_count=len(exported),
            message=f"Exported {len(exported)} journal entries",
        )
