#!/usr/bin/env python3
import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOTALS = ROOT / "data" / "raw" / "space_market_totals.csv"
SHARES = ROOT / "data" / "raw" / "layer_share_assumptions.csv"
SOURCE_PRIORITY = ROOT / "data" / "source_priority.csv"
OUT = ROOT / "data" / "processed" / "layer_market_timeseries.csv"


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_date(value: str):
    try:
        return date.fromisoformat(value)
    except ValueError:
        return date(1970, 1, 1)


def select_best(rows, priority_rank):
    return sorted(
        rows,
        key=lambda r: (
            priority_rank.get(r["source_type"], 999),
            -float(r["confidence"]),
            -parse_date(r["source_date"]).toordinal(),
        ),
    )[0]


def main() -> int:
    priority_rank = {r["source_type"]: int(r["priority_rank"]) for r in read_csv(SOURCE_PRIORITY)}
    total_candidates = read_csv(TOTALS)
    share_candidates = read_csv(SHARES)

    totals_by_year = defaultdict(list)
    for r in total_candidates:
        totals_by_year[int(r["year"])].append(r)
    totals = {year: select_best(rows, priority_rank) for year, rows in totals_by_year.items()}

    shares_by_key = defaultdict(list)
    for r in share_candidates:
        shares_by_key[(int(r["year"]), r["layer"])].append(r)
    selected_shares = [select_best(rows, priority_rank) for rows in shares_by_key.values()]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "year",
                "layer",
                "market_size_usd_billion",
                "share_ratio",
                "unit",
                "currency",
                "source_name",
                "source_url",
                "source_date",
                "method_note",
                "confidence",
            ],
        )
        writer.writeheader()

        for r in sorted(selected_shares, key=lambda x: (int(x["year"]), x["layer"])):
            year = int(r["year"])
            ratio = float(r["share_ratio"])
            total_row = totals[year]
            total = float(total_row["total_market_usd_billion"])

            combined_method = (
                f"Total({total_row['source_type']}): {total_row['method_note']} | "
                f"Layer split({r['source_type']}): {r['method_note']}"
            )
            combined_source = f"{total_row['source_name']} + {r['source_name']}"
            combined_source_url = f"{total_row['source_url']} | {r['source_url']}"
            combined_confidence = round((float(total_row["confidence"]) + float(r["confidence"])) / 2, 3)

            writer.writerow(
                {
                    "year": year,
                    "layer": r["layer"],
                    "market_size_usd_billion": f"{total * ratio:.3f}",
                    "share_ratio": f"{ratio:.6f}",
                    "unit": "billion",
                    "currency": "USD",
                    "source_name": combined_source,
                    "source_url": combined_source_url,
                    "source_date": total_row["source_date"],
                    "method_note": combined_method,
                    "confidence": f"{combined_confidence:.3f}",
                }
            )

    print(f"Wrote {OUT}")
    print(f"Selected totals: {len(totals)} years from {len(total_candidates)} candidates")
    print(f"Selected layer splits: {len(selected_shares)} from {len(share_candidates)} candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
