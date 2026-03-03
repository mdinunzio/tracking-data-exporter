import shutil
import subprocess
from datetime import date, datetime
from pathlib import Path
from typing import Any

from .exporters import EXPORTERS
from .exporters.base import ExportResult


def run_export(
    config: dict[str, Any],
    start_date: date,
    end_date: date,
    output_dir: Path | None = None,
    only: list[str] | None = None,
    exclude: list[str] | None = None,
    zip_output: bool = False,
    copy_prompt: bool = True,
    verbose: bool = False,
) -> Path:
    """Run all enabled exporters and produce the output package."""
    if output_dir is None:
        output_dir = Path(config["general"]["output_dir"]).expanduser()

    export_name = f"export-{date.today()}"
    export_dir = output_dir / export_name
    export_dir.mkdir(parents=True, exist_ok=True)

    results: list[ExportResult] = []

    for name, exporter_cls in EXPORTERS.items():
        # Filter by --only / --exclude
        if only and name not in only:
            continue
        if exclude and name in exclude:
            continue

        section_config = config.get(name, {})
        exporter = exporter_cls(section_config)

        if not exporter.enabled:
            results.append(ExportResult(
                source_name=exporter.display_name,
                success=True,
                message="Disabled in config",
            ))
            if verbose:
                _print_status("OFF", exporter.display_name, "Disabled in config")
            continue

        errors = exporter.validate_config()
        if errors:
            msg = "; ".join(errors)
            results.append(ExportResult(
                source_name=exporter.display_name,
                success=False,
                message=f"Config error: {msg}",
            ))
            _print_status("ERR", exporter.display_name, msg)
            continue

        try:
            result = exporter.export(start_date, end_date, export_dir)
            results.append(result)
            status = "OK" if result.success else "ERR"
            _print_status(status, exporter.display_name, result.message)
        except Exception as e:
            results.append(ExportResult(
                source_name=exporter.display_name,
                success=False,
                message=f"Error: {e}",
            ))
            _print_status("ERR", exporter.display_name, str(e))
            if verbose:
                import traceback
                traceback.print_exc()

    # Generate manifest
    _write_manifest(export_dir, start_date, end_date, results)

    # Zip if requested
    final_path = export_dir
    if zip_output:
        zip_path = shutil.make_archive(str(export_dir), "zip", output_dir, export_name)
        shutil.rmtree(export_dir)
        final_path = Path(zip_path)
        print(f"\nExport saved to: {final_path}")
    else:
        print(f"\nExport saved to: {final_path}/")

    # Copy prompt to clipboard
    if copy_prompt:
        prompt_file = config["general"].get("prompt_file", "")
        if prompt_file:
            _copy_prompt_to_clipboard(Path(prompt_file))

    return final_path


def _write_manifest(
    export_dir: Path,
    start_date: date,
    end_date: date,
    results: list[ExportResult],
) -> None:
    lines = [
        "# Tracking Data Export",
        f"**Period:** {start_date} to {end_date}",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Sources",
        "| Source | Status | Records | Notes |",
        "|--------|--------|---------|-------|",
    ]

    for r in results:
        if r.success and r.record_count > 0:
            status = "OK"
        elif r.success:
            status = "SKIPPED"
        else:
            status = "ERROR"
        count = str(r.record_count) if r.record_count else "-"
        lines.append(f"| {r.source_name} | {status} | {count} | {r.message} |")

    lines.append("")
    manifest = export_dir / "manifest.md"
    manifest.write_text("\n".join(lines))


def _copy_prompt_to_clipboard(prompt_path: Path) -> None:
    if not prompt_path.is_file():
        print(f"Warning: Prompt file not found: {prompt_path}")
        return
    try:
        text = prompt_path.read_text()
        subprocess.run(["pbcopy"], input=text.encode(), check=True)
        print("Life coach prompt copied to clipboard.")
    except FileNotFoundError:
        print("Warning: pbcopy not available (macOS only)")
    except subprocess.CalledProcessError:
        print("Warning: Failed to copy prompt to clipboard")


def _print_status(status: str, name: str, message: str) -> None:
    colors = {
        "OK": "\033[32m",
        "ERR": "\033[31m",
        "OFF": "\033[90m",
        "SKIP": "\033[33m",
    }
    reset = "\033[0m"
    color = colors.get(status, "")
    print(f"  {color}[{status:>4}]{reset} {name}: {message}")
