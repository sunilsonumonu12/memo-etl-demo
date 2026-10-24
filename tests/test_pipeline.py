import csv
import json
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline import parse_order_date, process_orders


class ParseDateTests(unittest.TestCase):
    def test_iso_date_is_normalized(self):
        self.assertEqual(parse_order_date("2026-10-01"), "2026-10-01")

    def test_multiple_date_formats_are_normalized(self):
        self.assertEqual(parse_order_date("2026/10/03"), "2026-10-03")
        self.assertEqual(parse_order_date("02-10-2026"), "2026-10-02")


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.input_path = self.root / "orders.csv"
        self.output_dir = self.root / "out"
        rows = [
            {"order_id": "O-1", "customer_id": "C-1", "order_date": "2026-10-01", "amount": "100.00", "status": "COMPLETED"},
            {"order_id": "O-1", "customer_id": "C-1", "order_date": "2026-10-01", "amount": "100.00", "status": "COMPLETED"},
            {"order_id": "O-2", "customer_id": "C-2", "order_date": "2026-10-02", "amount": "50.00", "status": "CANCELLED"},
        ]
        with self.input_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["order_id", "customer_id", "order_date", "amount", "status"])
            writer.writeheader()
            writer.writerows(rows)

    def tearDown(self):
        self.temp.cleanup()

    def read_clean(self):
        with (self.output_dir / "clean_orders.csv").open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def test_duplicate_order_ids_keep_first_occurrence(self):
        process_orders(self.input_path, self.output_dir)
        rows = self.read_clean()
        ids = [row["order_id"] for row in rows]
        self.assertEqual(ids.count("O-1"), 1)

    def test_cancelled_orders_are_excluded_from_clean_output_and_revenue(self):
        summary = process_orders(self.input_path, self.output_dir)
        rows = self.read_clean()
        self.assertTrue(all(row["status"] != "CANCELLED" for row in rows))
        self.assertEqual(summary["total_revenue"], "100.00")

    def test_summary_json_matches_return_value(self):
        result = process_orders(self.input_path, self.output_dir)
        saved = json.loads((self.output_dir / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(saved, result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
