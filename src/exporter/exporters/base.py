from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any


@dataclass
class ExportResult:
    """Result from running an exporter."""
    source_name: str
    success: bool
    files_exported: list[Path] = field(default_factory=list)
    record_count: int = 0
    message: str = ""


class BaseExporter(ABC):
    """Base class all exporters must implement."""

    name: str = ""
    display_name: str = ""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", False)

    @abstractmethod
    def validate_config(self) -> list[str]:
        """Return list of config errors. Empty list = valid."""
        ...

    @abstractmethod
    def export(self, start_date: date, end_date: date, output_dir: Path) -> ExportResult:
        """Export data for the given date range into output_dir."""
        ...
