import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

from .config import load_config
from .exporters import EXPORTERS
from .runner import run_export

DEFAULT_CONFIG_PATHS = [
    Path("config.toml"),
    Path.home() / ".config" / "tracking-exporter" / "config.toml",
]


def find_config(explicit_path: str | None = None) -> Path:
    if explicit_path:
        p = Path(explicit_path)
        if not p.exists():
            print(f"Error: Config file not found: {p}", file=sys.stderr)
            sys.exit(1)
        return p
    for p in DEFAULT_CONFIG_PATHS:
        if p.exists():
            return p
    print(
        "Error: No config.toml found. Copy config.example.toml to config.toml and edit it.",
        file=sys.stderr,
    )
    sys.exit(1)


def parse_date(s: str) -> date:
    try:
        return date.fromisoformat(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date: {s} (expected YYYY-MM-DD)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gather tracking data for life coach LLM upload.",
    )
    parser.add_argument("--days", type=int, help="Number of days to export (default: from config, usually 7)")
    parser.add_argument("--from", dest="from_date", type=parse_date, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to", dest="to_date", type=parse_date, help="End date (YYYY-MM-DD, default: today)")
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--output-dir", help="Output directory (overrides config)")
    parser.add_argument("--only", nargs="+", choices=list(EXPORTERS.keys()), help="Run only these exporters")
    parser.add_argument("--exclude", nargs="+", choices=list(EXPORTERS.keys()), help="Skip these exporters")
    parser.add_argument("--no-zip", action="store_true", help="Output as directory instead of zip")
    parser.add_argument("--no-prompt-copy", action="store_true", help="Don't copy prompt to clipboard")
    parser.add_argument("--list-sources", action="store_true", help="List available exporters and exit")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    config_path = find_config(args.config)
    config = load_config(config_path)

    if args.list_sources:
        _list_sources(config)
        return

    # Determine date range
    end_date = args.to_date or date.today()
    if args.from_date:
        start_date = args.from_date
    else:
        days = args.days or config["general"]["default_days"]
        start_date = end_date - timedelta(days=days - 1)

    print(f"Exporting data from {start_date} to {end_date}\n")

    output_dir = Path(args.output_dir) if args.output_dir else None

    run_export(
        config=config,
        start_date=start_date,
        end_date=end_date,
        output_dir=output_dir,
        only=args.only,
        exclude=args.exclude,
        zip_output=not args.no_zip,
        copy_prompt=not args.no_prompt_copy,
        verbose=args.verbose,
    )


def _list_sources(config: dict) -> None:
    print("Available exporters:\n")
    for name, cls in EXPORTERS.items():
        section = config.get(name, {})
        enabled = section.get("enabled", False)
        exporter = cls(section)
        errors = exporter.validate_config() if enabled else []
        if enabled and not errors:
            status = "\033[32mENABLED\033[0m"
        elif enabled:
            status = f"\033[31mERROR: {'; '.join(errors)}\033[0m"
        else:
            status = "\033[90mDISABLED\033[0m"
        print(f"  {name:<20} {cls.display_name:<30} {status}")
