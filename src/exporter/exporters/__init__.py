from .apple_health import AppleHealthExporter
from .google_calendar import GoogleCalendarExporter
from .google_sheets import GoogleSheetsExporter
from .obsidian import ObsidianExporter
from .streaks import StreaksExporter
from .ynab import YnabExporter

EXPORTERS = {
    "obsidian": ObsidianExporter,
    "google_sheets": GoogleSheetsExporter,
    "ynab": YnabExporter,
    "streaks": StreaksExporter,
    "apple_health": AppleHealthExporter,
    "google_calendar": GoogleCalendarExporter,
}
