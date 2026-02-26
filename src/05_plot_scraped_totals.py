#!/usr/bin/env python3
import csv
import re
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
IN_VALUES = ROOT / "data" / "raw" / "scraped_market_values.csv"
IN_SOURCES = ROOT / "data" / "raw" / "scraped_source_registry.csv"
OUT_PNG = ROOT / "outputs" / "space_market_by_year_from_scraped.png"
OUT_CSV = ROOT / "data" / "processed" / "space_market_totals_from_scraped.csv"


def release_year_from_url(url: str) -> int:
    m = re.search(r"/([0-9]{4})/", url)
    return int(m.group(1)) if m else 0


def load_sources(path: Path):
    mapping = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            mapping[row["source_id"]] = {
                "source_url": row["source_url"],
                "source_name": row["source_name"],
                "status": row["status"],
                "release_year": release_year_from_url(row["source_url"]),
            }
    return mapping


def main() -> int:
    sources = load_sources(IN_SOURCES)

    candidates = {}
    with IN_VALUES.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["layer"] != "total_space_economy":
                continue
            if row["unit"] != "billion" or row["currency"] != "USD":
                continue
            if row["is_forecast"].lower() == "true":
                continue

            year = int(row["year"])
            source_id = row["source_id"]
            source = sources.get(source_id, {})
            tier = row["source_tier"]
            tier_rank = 0 if tier == "primary_official" else 1
            release_year = source.get("release_year", 0)
            confidence = 1.0 if tier == "primary_official" else 0.5

            candidate = {
                "year": year,
                "value": float(row["value"]),
                "source_id": source_id,
                "source_name": source.get("source_name", ""),
                "source_url": row["source_url"],
                "release_year": release_year,
                "tier": tier,
            }
            sort_key = (tier_rank, -release_year, -confidence)

            if year not in candidates or sort_key < candidates[year]["sort_key"]:
                candidate["sort_key"] = sort_key
                candidates[year] = candidate

    selected = [candidates[y] for y in sorted(candidates)]

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "year",
                "total_market_usd_billion",
                "source_id",
                "source_name",
                "source_url",
                "source_tier",
                "release_year",
                "selection_rule",
            ],
        )
        writer.writeheader()
        for r in selected:
            writer.writerow(
                {
                    "year": r["year"],
                    "total_market_usd_billion": f"{r['value']:.1f}",
                    "source_id": r["source_id"],
                    "source_name": r["source_name"],
                    "source_url": r["source_url"],
                    "source_tier": r["tier"],
                    "release_year": r["release_year"],
                    "selection_rule": "prefer primary_official; then newer release year",
                }
            )

    years = [r["year"] for r in selected]
    values = [r["value"] for r in selected]

    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = [
        "Hiragino Sans",
        "Yu Gothic",
        "Noto Sans CJK JP",
        "IPAexGothic",
        "TakaoGothic",
        "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False

    plt.figure(figsize=(10, 5.8))
    plt.plot(
        years,
        values,
        marker="o",
        linewidth=2.2,
        color="#1f77b4",
        label="世界宇宙経済の市場規模",
    )
    for x, y in zip(years, values):
        plt.text(x, y + 4, f"{y:.0f}", ha="center", va="bottom", fontsize=9)

    plt.title("年度別 世界宇宙経済市場規模（Space Foundation抽出値）")
    plt.xlabel("年度")
    plt.ylabel("市場規模（十億USD）")
    plt.legend(title="系列", loc="upper left")
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()

    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUT_PNG, dpi=180)
    plt.close()

    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_PNG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
