# Final acceptance criteria

After all three seeded bugs are fixed:

- All unit tests pass.
- The sample CSV yields 4 accepted completed orders after ignoring the duplicate row and filtering cancelled rows. Invalid missing-customer, invalid-date, and negative-amount records are quarantined. Note: date variants must be parsed before business rules are fully applied.
- The final accepted sample should contain O-1001, O-1002, O-1003, and O-1008 only.
- Total revenue should be 2750.50 (1200.00 + 850.50 + 600.00 + 100.00).
- Cancelled O-1004 must not appear in `clean_orders.csv` or revenue totals.
- The same `order_id` should appear at most once, keeping the first valid occurrence.

The initial unit-test fixture is separate from `data/raw/orders.csv`, so the unit tests isolate each bug.
