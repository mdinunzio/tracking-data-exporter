import csv
from datetime import date
from pathlib import Path
from typing import Any

import httpx

from .base import BaseExporter, ExportResult


class GoogleCalendarExporter(BaseExporter):
    name = "google_calendar"
    display_name = "Google Calendar"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key", "")
        self.calendar_ids = config.get("calendar_ids", ["primary"])

    def validate_config(self) -> list[str]:
        errors = []
        if not self.api_key:
            errors.append("google_calendar.api_key is required")
        return errors

    def export(self, start_date: date, end_date: date, output_dir: Path) -> ExportResult:
        dest = output_dir / "calendar"
        dest.mkdir(parents=True, exist_ok=True)

        all_events = []
        for cal_id in self.calendar_ids:
            url = f"https://www.googleapis.com/calendar/v3/calendars/{cal_id}/events"
            params = {
                "key": self.api_key,
                "timeMin": f"{start_date}T00:00:00Z",
                "timeMax": f"{end_date}T23:59:59Z",
                "singleEvents": "true",
                "orderBy": "startTime",
                "maxResults": 250,
            }
            try:
                resp = httpx.get(url, params=params, timeout=30)
                resp.raise_for_status()
                items = resp.json().get("items", [])
                all_events.extend(items)
            except httpx.HTTPStatusError as e:
                return ExportResult(
                    source_name=self.display_name,
                    success=False,
                    message=f"API error for calendar {cal_id}: {e.response.status_code}",
                )

        if not all_events:
            return ExportResult(
                source_name=self.display_name,
                success=True,
                message="No events found in date range",
            )

        path = dest / "events.csv"
        fields = ["date", "start_time", "end_time", "summary"]
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for event in all_events:
                start = event.get("start", {})
                end_dt = event.get("end", {})
                writer.writerow({
                    "date": start.get("date", start.get("dateTime", "")[:10]),
                    "start_time": start.get("dateTime", ""),
                    "end_time": end_dt.get("dateTime", ""),
                    "summary": event.get("summary", "(No title)"),
                })

        return ExportResult(
            source_name=self.display_name,
            success=True,
            files_exported=[path],
            record_count=len(all_events),
            message=f"Exported {len(all_events)} events",
        )
