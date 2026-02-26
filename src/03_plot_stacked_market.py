#!/usr/bin/env python3
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_CSV = ROOT / "data" / "processed" / "layer_market_timeseries.csv"
OUT_SVG = ROOT / "outputs" / "market_stack_by_year.svg"
OUT_PNG = ROOT / "outputs" / "market_stack_by_year.png"

LAYER_ORDER = [
    "transport_launch",
    "satellite_infrastructure",
    "downstream_data_services",
    "in_orbit_services",
    "deep_space_lunar",
]
LAYER_LABELS = {
    "transport_launch": "Transport/Launch",
    "satellite_infrastructure": "Satellite Infrastructure",
    "downstream_data_services": "Downstream Data Services",
    "in_orbit_services": "In-Orbit Services",
    "deep_space_lunar": "Deep Space/Lunar",
}
COLORS = {
    "transport_launch": "#2f6d9b",
    "satellite_infrastructure": "#4fa3d1",
    "downstream_data_services": "#7bc96f",
    "in_orbit_services": "#f2c14e",
    "deep_space_lunar": "#f28e2b",
}


def read_data():
    rows = []
    with IN_CSV.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(
                {
                    "year": int(r["year"]),
                    "layer": r["layer"],
                    "value": float(r["market_size_usd_billion"]),
                }
            )
    return rows


def write_svg(series_by_year):
    years = sorted(series_by_year.keys())
    max_total = max(sum(series_by_year[y].values()) for y in years)

    width = 1080
    height = 620
    left = 90
    right = 300
    top = 50
    bottom = 85
    plot_w = width - left - right
    plot_h = height - top - bottom
    bar_w = int(plot_w / (len(years) * 1.7))

    def y_scale(v):
        return top + plot_h - (v / max_total) * plot_h

    OUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    with OUT_SVG.open("w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">\n')
        f.write('<rect width="100%" height="100%" fill="#f7fbff"/>\n')
        f.write('<text x="90" y="30" font-size="20" font-family="Arial" fill="#17324a">Space Market by Year (5-layer stacked)</text>\n')

        for i in range(6):
            v = max_total * i / 5
            y = y_scale(v)
            f.write(f'<line x1="{left}" y1="{y:.2f}" x2="{left+plot_w}" y2="{y:.2f}" stroke="#d7e4f1" stroke-width="1"/>\n')
            f.write(f'<text x="20" y="{y+5:.2f}" font-size="12" font-family="Arial" fill="#49667f">{v:.0f}</text>\n')

        for idx, year in enumerate(years):
            x = left + int((idx + 0.6) * (plot_w / len(years)))
            y_base = top + plot_h
            cumulative = 0.0
            for layer in LAYER_ORDER:
                v = series_by_year[year][layer]
                y1 = y_scale(cumulative + v)
                y2 = y_scale(cumulative)
                h = y2 - y1
                f.write(
                    f'<rect x="{x}" y="{y1:.2f}" width="{bar_w}" height="{h:.2f}" '
                    f'fill="{COLORS[layer]}"/>\n'
                )
                cumulative += v
            f.write(
                f'<text x="{x + bar_w/2:.2f}" y="{y_base + 20}" text-anchor="middle" '
                f'font-size="12" font-family="Arial" fill="#37556f">{year}</text>\n'
            )
            f.write(
                f'<text x="{x + bar_w/2:.2f}" y="{y_scale(cumulative)-6:.2f}" text-anchor="middle" '
                f'font-size="11" font-family="Arial" fill="#17324a">{cumulative:.1f}</text>\n'
            )

        lx = left + plot_w + 25
        ly = 90
        for layer in LAYER_ORDER:
            f.write(f'<rect x="{lx}" y="{ly}" width="16" height="16" fill="{COLORS[layer]}"/>\n')
            f.write(
                f'<text x="{lx+24}" y="{ly+13}" font-size="12" font-family="Arial" '
                f'fill="#17324a">{LAYER_LABELS[layer]}</text>\n'
            )
            ly += 28

        f.write('<text x="20" y="45" font-size="12" font-family="Arial" fill="#49667f">USD (billion)</text>\n')
        f.write('</svg>\n')


def try_write_png(series_by_year):
    try:
        import matplotlib.pyplot as plt
    except Exception:
        print("matplotlib not available; skipped PNG")
        return

    years = sorted(series_by_year.keys())
    bottom = [0.0] * len(years)
    fig, ax = plt.subplots(figsize=(11, 6))

    for layer in LAYER_ORDER:
        values = [series_by_year[y][layer] for y in years]
        ax.bar(years, values, bottom=bottom, label=LAYER_LABELS[layer], color=COLORS[layer])
        bottom = [b + v for b, v in zip(bottom, values)]

    ax.set_title("Space Market by Year (5-layer stacked)")
    ax.set_ylabel("USD (billion)")
    ax.legend(loc="center left", bbox_to_anchor=(1.0, 0.5))
    fig.tight_layout()
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PNG, dpi=160)
    plt.close(fig)
    print(f"Wrote {OUT_PNG}")


def main() -> int:
    rows = read_data()
    series_by_year = defaultdict(dict)
    for r in rows:
        series_by_year[r["year"]][r["layer"]] = r["value"]

    write_svg(series_by_year)
    print(f"Wrote {OUT_SVG}")
    try_write_png(series_by_year)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
