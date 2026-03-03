import csv
from datetime import date
from pathlib import Path
from typing import Any

import httpx

from .base import BaseExporter, ExportResult


class GoogleSheetsExporter(BaseExporter):
    name = "google_sheets"
    display_name = "Weight Tracking (Google Sheets)"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.spreadsheet_id = config.get("spreadsheet_id", "")
        self.sheet_range = config.get("sheet_range", "Sheet1!A:Z")
        self.api_key = config.get("api_key", "")

    def validate_config(self) -> list[str]:
        errors = []
        if not self.spreadsheet_id:
            errors.append("google_sheets.spreadsheet_id is required")
        if not self.api_key:
            errors.append("google_sheets.api_key is required")
        return errors

    def export(self, start_date: date, end_date: date, output_dir: Path) -> ExportResult:
        dest = output_dir / "weight"
        dest.mkdir(parents=True, exist_ok=True)

        url = (
            f"https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}"
            f"/values/{self.sheet_range}"
        )
        try:
            resp = httpx.get(url, params={"key": self.api_key}, timeout=30)
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            return ExportResult(
                source_name=self.display_name,
                success=False,
                message=f"API error: {e.response.status_code}",
            )

        data = resp.json()
        rows = data.get("values", [])
        if not rows:
            return ExportResult(
                source_name=self.display_name,
                success=True,
                message="No data found in spreadsheet",
            )

        # Write all rows as CSV (header + data)
        path = dest / "weight-data.csv"
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)

        data_rows = len(rows) - 1 if len(rows) > 1 else len(rows)
        return ExportResult(
            source_name=self.display_name,
            success=True,
            files_exported=[path],
            record_count=data_rows,
            message=f"Exported {data_rows} rows",
        )
