"""Training ETL pipeline. Three intentional bugs are left for the MEMO demo."""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "raw" / "orders.csv"
OUTPUT_DIR = ROOT / "data" / "processed"
FIELDS = ["order_id", "customer_id", "order_date", "amount", "status"]


def parse_order_date(value: str) -> str:
    """Return ISO date string. BUG 1: currently accepts only ISO dates."""
    return datetime.strptime(value.strip(), "%Y-%m-%d").date().isoformat()


def process_orders(input_path: Path = INPUT, output_dir: Path = OUTPUT_DIR) -> dict:
    clean: list[dict[str, str]] = []
    rejected: list[dict[str, str]] = []

    with input_path.open(newline="", encoding="utf-8") as handle:
        for line_no, row in enumerate(csv.DictReader(handle), start=2):
            order_id = (row.get("order_id") or "").strip()
            customer_id = (row.get("customer_id") or "").strip()
            status = (row.get("status") or "").strip().upper()

            if not order_id:
                rejected.append({"line": str(line_no), "reason": "missing_order_id", **row})
                continue
            if not customer_id:
                rejected.append({"line": str(line_no), "reason": "missing_customer_id", **row})
                continue

            try:
                order_date = parse_order_date(row.get("order_date") or "")
            except ValueError:
                rejected.append({"line": str(line_no), "reason": "invalid_order_date", **row})
                continue

            try:
                amount = Decimal((row.get("amount") or "").strip())
            except InvalidOperation:
                rejected.append({"line": str(line_no), "reason": "invalid_amount", **row})
                continue
            if amount <= 0:
                rejected.append({"line": str(line_no), "reason": "amount_must_be_positive", **row})
                continue

            # BUG 2: duplicate order IDs are not detected; every row is accepted.
            # BUG 3: CANCELLED orders are not filtered out of the accepted dataset.
            clean.append({
                "order_id": order_id,
                "customer_id": customer_id,
                "order_date": order_date,
                "amount": f"{amount:.2f}",
                "status": status,
            })

    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "clean_orders.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(clean)

    revenue_by_customer: dict[str, Decimal] = defaultdict(Decimal)
    revenue_by_month: dict[str, Decimal] = defaultdict(Decimal)
    for order in clean:
        value = Decimal(order["amount"])
        revenue_by_customer[order["customer_id"]] += value
        revenue_by_month[order["order_date"][:7]] += value

    total = sum((Decimal(row["amount"]) for row in clean), Decimal("0.00"))
    summary = {
        "accepted_rows": len(clean),
        "rejected_rows": len(rejected),
        "total_revenue": f"{total:.2f}",
        "revenue_by_customer": {k: f"{v:.2f}" for k, v in sorted(revenue_by_customer.items())},
        "revenue_by_month": {k: f"{v:.2f}" for k, v in sorted(revenue_by_month.items())},
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with (output_dir / "rejected_orders.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["line", "reason", *FIELDS])
        writer.writeheader()
        writer.writerows(rejected)

    return summary


if __name__ == "__main__":
    result = process_orders()
    print(json.dumps(result, indent=2))
