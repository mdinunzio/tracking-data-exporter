import csv
from datetime import date
from pathlib import Path
from typing import Any

import httpx

from .base import BaseExporter, ExportResult

BASE_URL = "https://api.ynab.com/v1"


class YnabExporter(BaseExporter):
    name = "ynab"
    display_name = "YNAB Budget"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.access_token = config.get("access_token", "")
        self.budget_id = config.get("budget_id", "last-used")

    def validate_config(self) -> list[str]:
        errors = []
        if not self.access_token:
            errors.append("ynab.access_token is required (get one at https://app.ynab.com/settings/developer)")
        return errors

    def _get(self, path: str, params: dict | None = None) -> dict:
        headers = {"Authorization": f"Bearer {self.access_token}"}
        resp = httpx.get(f"{BASE_URL}{path}", headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()["data"]

    def export(self, start_date: date, end_date: date, output_dir: Path) -> ExportResult:
        dest = output_dir / "ynab"
        dest.mkdir(parents=True, exist_ok=True)
        exported: list[Path] = []
        total_records = 0

        # Transactions
        try:
            data = self._get(
                f"/budgets/{self.budget_id}/transactions",
                params={"since_date": start_date.isoformat()},
            )
            transactions = [
                t for t in data["transactions"]
                if t["date"] <= end_date.isoformat()
            ]
            if transactions:
                path = dest / "transactions.csv"
                _write_transactions_csv(path, transactions)
                exported.append(path)
                total_records += len(transactions)
        except httpx.HTTPStatusError as e:
            return ExportResult(
                source_name=self.display_name,
                success=False,
                message=f"API error fetching transactions: {e.response.status_code}",
            )

        # Accounts
        try:
            data = self._get(f"/budgets/{self.budget_id}/accounts")
            accounts = [a for a in data["accounts"] if not a.get("deleted")]
            if accounts:
                path = dest / "accounts.csv"
                _write_accounts_csv(path, accounts)
                exported.append(path)
        except httpx.HTTPStatusError:
            pass  # Non-critical

        # Categories
        try:
            data = self._get(f"/budgets/{self.budget_id}/categories")
            categories = []
            for group in data["category_groups"]:
                if group.get("deleted"):
                    continue
                for cat in group.get("categories", []):
                    if cat.get("deleted") or cat.get("hidden"):
                        continue
                    cat["group_name"] = group["name"]
                    categories.append(cat)
            if categories:
                path = dest / "categories.csv"
                _write_categories_csv(path, categories)
                exported.append(path)
        except httpx.HTTPStatusError:
            pass  # Non-critical

        return ExportResult(
            source_name=self.display_name,
            success=True,
            files_exported=exported,
            record_count=total_records,
            message=f"Exported {total_records} transactions, {len(exported)} files",
        )


def _milliunits_to_dollars(milliunits: int) -> str:
    return f"{milliunits / 1000:.2f}"


def _write_transactions_csv(path: Path, transactions: list[dict]) -> None:
    fields = ["date", "account_name", "payee_name", "category_name", "memo", "amount"]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for t in transactions:
            writer.writerow({
                "date": t["date"],
                "account_name": t.get("account_name", ""),
                "payee_name": t.get("payee_name", ""),
                "category_name": t.get("category_name", ""),
                "memo": t.get("memo", "") or "",
                "amount": _milliunits_to_dollars(t["amount"]),
            })


def _write_accounts_csv(path: Path, accounts: list[dict]) -> None:
    fields = ["name", "type", "balance", "cleared_balance", "uncleared_balance"]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for a in accounts:
            writer.writerow({
                "name": a["name"],
                "type": a["type"],
                "balance": _milliunits_to_dollars(a["balance"]),
                "cleared_balance": _milliunits_to_dollars(a["cleared_balance"]),
                "uncleared_balance": _milliunits_to_dollars(a["uncleared_balance"]),
            })


def _write_categories_csv(path: Path, categories: list[dict]) -> None:
    fields = ["group", "name", "budgeted", "activity", "balance"]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for c in categories:
            writer.writerow({
                "group": c.get("group_name", ""),
                "name": c["name"],
                "budgeted": _milliunits_to_dollars(c.get("budgeted", 0)),
                "activity": _milliunits_to_dollars(c.get("activity", 0)),
                "balance": _milliunits_to_dollars(c.get("balance", 0)),
            })
