import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

from .base import BaseExporter, ExportResult

DATE_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")


class AppleHealthExporter(BaseExporter):
    name = "apple_health"
    display_name = "Apple Health"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.vault_path = Path(config.get("vault_path", ""))

    def validate_config(self) -> list[str]:
        errors = []
        if not self.vault_path:
            errors.append("apple_health.vault_path is required")
        elif not self.vault_path.is_dir():
            errors.append(
                f"apple_health.vault_path does not exist: "
                f"{self.vault_path}"
            )
        return errors

    def export(
        self,
        start_date: date,
        end_date: date,
        output_dir: Path,
    ) -> ExportResult:
        parts: list[str] = []
        count = 0

        for entry in sorted(self.vault_path.iterdir()):
            if not entry.is_file():
                continue
            match = DATE_PATTERN.match(entry.name)
            if not match:
                continue
            file_date = datetime.strptime(
                match.group(1), "%Y-%m-%d"
            ).date()
            if start_date <= file_date <= end_date:
                text = entry.read_text(errors="replace")
                parts.append(f"# {file_date}\n\n{text}")
                count += 1

        if not parts:
            return ExportResult(
                source_name=self.display_name,
                success=True,
                message=(
                    f"No health entries found for "
                    f"{start_date} to {end_date}"
                ),
            )

        out_file = output_dir / "Health.md"
        out_file.write_text("\n\n---\n\n".join(parts))

        return ExportResult(
            source_name=self.display_name,
            success=True,
            files_exported=[out_file],
            record_count=count,
            message=f"Concatenated {count} days into Health.md",
        )
