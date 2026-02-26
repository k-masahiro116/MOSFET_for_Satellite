#!/usr/bin/env python3
import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOTALS = ROOT / "data" / "raw" / "space_market_totals.csv"
SHARES = ROOT / "data" / "raw" / "layer_share_assumptions.csv"
SOURCE_PRIORITY = ROOT / "data" / "source_priority.csv"

REQUIRED_TOTAL_COLS = {
    "year",
    "total_market_usd_billion",
    "source_name",
    "source_url",
    "source_date",
    "method_note",
    "confidence",
    "source_type",
}
REQUIRED_SHARE_COLS = {
    "year",
    "layer",
    "share_ratio",
    "source_name",
    "source_url",
    "source_date",
    "method_note",
    "confidence",
    "source_type",
}
REQUIRED_PRIORITY_COLS = {
    "source_type",
    "priority_rank",
    "description",
}
EXPECTED_LAYERS = {
    "transport_launch",
    "satellite_infrastructure",
    "downstream_data_services",
    "in_orbit_services",
    "deep_space_lunar",
}


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def validate_columns(rows, required, file_label):
    if not rows:
        raise ValueError(f"{file_label}: empty file")
    cols = set(rows[0].keys())
    missing = required - cols
    if missing:
        raise ValueError(f"{file_label}: missing columns {sorted(missing)}")


def main() -> int:
    totals = read_csv(TOTALS)
    shares = read_csv(SHARES)
    priorities = read_csv(SOURCE_PRIORITY)

    validate_columns(totals, REQUIRED_TOTAL_COLS, "space_market_totals.csv")
    validate_columns(shares, REQUIRED_SHARE_COLS, "layer_share_assumptions.csv")
    validate_columns(priorities, REQUIRED_PRIORITY_COLS, "source_priority.csv")
    allowed_source_types = {r["source_type"] for r in priorities}

    total_years = set()
    total_rows_by_year = defaultdict(int)
    for row in totals:
        year = int(row["year"])
        total = float(row["total_market_usd_billion"])
        conf = float(row["confidence"])
        source_type = row["source_type"]
        if total <= 0:
            raise ValueError(f"total must be positive: year={year}")
        if not 0 <= conf <= 1:
            raise ValueError(f"confidence out of range in totals: year={year}")
        if source_type not in allowed_source_types:
            raise ValueError(f"unknown source_type in totals: year={year}, source_type={source_type}")
        total_years.add(year)
        total_rows_by_year[year] += 1

    share_sums = defaultdict(float)
    layers_by_year = defaultdict(set)
    share_rows_by_key = defaultdict(int)
    for row in shares:
        year = int(row["year"])
        layer = row["layer"]
        ratio = float(row["share_ratio"])
        conf = float(row["confidence"])
        source_type = row["source_type"]

        if layer not in EXPECTED_LAYERS:
            raise ValueError(f"unexpected layer={layer} year={year}")
        if not 0 <= ratio <= 1:
            raise ValueError(f"share ratio out of range: year={year}, layer={layer}")
        if not 0 <= conf <= 1:
            raise ValueError(f"confidence out of range in shares: year={year}, layer={layer}")
        if source_type not in allowed_source_types:
            raise ValueError(f"unknown source_type in shares: year={year}, layer={layer}, source_type={source_type}")

        share_sums[year] += ratio
        layers_by_year[year].add(layer)
        share_rows_by_key[(year, layer)] += 1

    for year in sorted(total_years):
        if year not in share_sums:
            raise ValueError(f"missing layer shares for year={year}")
        if abs(share_sums[year] - 1.0) > 1e-6:
            raise ValueError(f"share sum must be 1.0: year={year}, got={share_sums[year]:.6f}")
        if layers_by_year[year] != EXPECTED_LAYERS:
            missing = EXPECTED_LAYERS - layers_by_year[year]
            raise ValueError(f"missing layers for year={year}: {sorted(missing)}")

    extra_years = set(share_sums.keys()) - total_years
    if extra_years:
        raise ValueError(f"years in shares but not totals: {sorted(extra_years)}")

    print("Validation passed")
    print(f"Years: {sorted(total_years)}")
    duplicate_totals = sum(1 for _, count in total_rows_by_year.items() if count > 1)
    duplicate_shares = sum(1 for _, count in share_rows_by_key.items() if count > 1)
    print(f"Duplicate candidates (totals by year): {duplicate_totals}")
    print(f"Duplicate candidates (shares by year+layer): {duplicate_shares}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
