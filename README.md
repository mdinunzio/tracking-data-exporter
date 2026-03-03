# Tracking Data Exporter

CLI tool that gathers tracking data from multiple sources and packages it into a folder for upload to a life coach LLM.

After export, the life coach system prompt is copied to your clipboard — just paste it into the LLM conversation and upload the files.

## Setup

```bash
# Install dependencies
uv sync

# Create your config from the example
cp config.example.toml config.toml
# Edit config.toml to set your paths and API keys
```

## Usage

```bash
uv run export-data                          # Past 30 days, all enabled sources
uv run export-data --days 7                 # Past 7 days
uv run export-data --from 2026-02-01 --to 2026-02-14  # Specific date range
uv run export-data --only obsidian ynab     # Just these sources
uv run export-data --list-sources           # Show what's configured
uv run export-data --zip                    # Output as zip instead of folder
uv run export-data --verbose                # Show disabled sources and errors
```

Output goes to `~/Downloads/export-{date}/` by default.

## Data Sources

| Source | Type | Config needed |
|--------|------|---------------|
| **Obsidian Journals** | Local `.md` files → `Journal.md` | `vault_path` |
| **Apple Health** | Local `.md` files → `Health.md` | `vault_path` (Health.md app syncs via iCloud) |
| **YNAB** | API | `access_token` — [YNAB Developer Settings](https://app.ynab.com/settings/developer) |
| **Google Sheets** (weight) | API | `api_key` + `spreadsheet_id` — [Google Cloud Console](https://console.cloud.google.com/apis/credentials) |
| **Streaks** | Pickup file | Apple Shortcut exports to a pickup directory |
| **Google Calendar** | API | `api_key` + `calendar_ids` — same Google API key as Sheets |

Each source has an `enabled` flag in `config.toml`. Disabled or misconfigured sources are skipped gracefully.

## Output Structure

```
~/Downloads/export-2026-03-03/
├── manifest.md              # LLM-readable summary of what's included
├── Journal.md               # Concatenated Obsidian daily journals
├── Health.md                # Concatenated Apple Health daily entries
├── ynab/
│   ├── transactions.csv     # Transactions for the period
│   ├── accounts.csv         # Account balances
│   └── categories.csv       # Category budgets/balances
├── weight/
│   └── weight-data.csv      # From Google Sheets
├── streaks/                 # Habit tracking export
└── calendar/
    └── events.csv           # Calendar events
```

## Apple Shortcuts (for Streaks)

The Streaks exporter uses a "pickup file" pattern — an Apple Shortcut exports data to iCloud Drive, and the tool picks it up. See [shortcuts/README.md](shortcuts/README.md) for setup instructions.
