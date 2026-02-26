#!/usr/bin/env python3
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_CSV = ROOT / "data" / "processed" / "layer_market_timeseries.csv"
OUT_MD = ROOT / "outputs" / "analysis_summary.md"

LAYERS = [
    "transport_launch",
    "satellite_infrastructure",
    "downstream_data_services",
    "in_orbit_services",
    "deep_space_lunar",
]
LAYER_JA = {
    "transport_launch": "輸送（ロケット）",
    "satellite_infrastructure": "衛星インフラ",
    "downstream_data_services": "ダウンストリーム（データ活用）",
    "in_orbit_services": "軌道上サービス",
    "deep_space_lunar": "深宇宙・月面開発",
}


def cagr(start, end, years):
    if start <= 0 or years <= 0:
        return 0.0
    return (end / start) ** (1 / years) - 1


def main() -> int:
    by_year = defaultdict(lambda: defaultdict(float))

    with IN_CSV.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            y = int(r["year"])
            layer = r["layer"]
            v = float(r["market_size_usd_billion"])
            by_year[y][layer] += v

    years = sorted(by_year.keys())
    totals = {y: sum(by_year[y].values()) for y in years}
    whole_cagr = cagr(totals[years[0]], totals[years[-1]], years[-1] - years[0])

    layer_growth = []
    for layer in LAYERS:
        start = by_year[years[0]][layer]
        end = by_year[years[-1]][layer]
        gr = cagr(start, end, years[-1] - years[0])
        abs_delta = end - start
        layer_growth.append((layer, gr, abs_delta))
    layer_growth.sort(key=lambda x: x[2], reverse=True)

    first = years[0]
    last = years[-1]
    has_2024_2026 = 2024 in totals and 2025 in totals and 2026 in totals
    if has_2024_2026:
        yoy_24_25 = (totals[2025] / totals[2024]) - 1
        yoy_25_26 = (totals[2026] / totals[2025]) - 1
        downstream_share_2026 = by_year[2026]["downstream_data_services"] / totals[2026]
        in_orbit_cagr_24_26 = cagr(by_year[2024]["in_orbit_services"], by_year[2026]["in_orbit_services"], 2)
        total_cagr_24_26 = cagr(totals[2024], totals[2026], 2)
    with OUT_MD.open("w", encoding="utf-8") as f:
        f.write("# 宇宙5レイヤー市場分析（初期版）\n\n")
        f.write("## 前提\n")
        f.write("- 本分析は `data/raw` の実測値と推計値を統合した初期シナリオ。\n")
        f.write("- 2024年は公開値、2025-2026年は内部推計を含む。\n\n")

        f.write("## 全体市場トレンド\n")
        f.write(f"- 対象期間: {first}年 - {last}年\n")
        f.write(f"- 市場規模: {totals[first]:.1f} -> {totals[last]:.1f} (USD billion)\n")
        f.write(f"- 期間CAGR: {whole_cagr*100:.2f}%\n\n")

        f.write("## レイヤー別増分（寄与順）\n")
        for layer, gr, delta in layer_growth:
            f.write(f"- {LAYER_JA[layer]}: 増分 {delta:.1f}, CAGR {gr*100:.2f}%\n")
        f.write("\n")

        f.write("## 最新年構成比\n")
        for layer in LAYERS:
            share = by_year[last][layer] / totals[last] if totals[last] else 0
            f.write(f"- {LAYER_JA[layer]}: {share*100:.1f}%\n")
        f.write("\n")

        f.write("## 解釈\n")
        lead = layer_growth[0][0]
        f.write(f"- 最大寄与は {LAYER_JA[lead]}。地上用途への展開が全体成長を牽引。\n")
        f.write("- 軌道上サービスは絶対額は小さいが、成長率が高く新興セグメントとして有望。\n")
        f.write("- 深宇宙・月面開発は構成比を維持しつつ、長サイクル投資として継続。\n\n")

        f.write("## 2025-2026整合チェック（space_research_report準拠）\n")
        if not has_2024_2026:
            f.write("- 判定不可: 2024-2026年の時系列が不足。\n\n")
        else:
            transition_ok = yoy_24_25 > 0 and yoy_25_26 > 0
            downstream_ok = downstream_share_2026 >= 0.50
            in_orbit_ok = in_orbit_cagr_24_26 > total_cagr_24_26
            f.write(
                f"- 商業運用フェーズ移行（市場拡大継続）: "
                f"{'整合' if transition_ok else '要確認'} "
                f"(2024->2025: {yoy_24_25*100:.2f}%, 2025->2026: {yoy_25_26*100:.2f}%)\n"
            )
            f.write(
                f"- ダウンストリーム成熟: "
                f"{'整合' if downstream_ok else '要確認'} "
                f"(2026構成比: {downstream_share_2026*100:.1f}%)\n"
            )
            f.write(
                f"- 軌道上サービスの立ち上がり: "
                f"{'整合' if in_orbit_ok else '要確認'} "
                f"(2024-2026 CAGR: {in_orbit_cagr_24_26*100:.2f}%, 全体: {total_cagr_24_26*100:.2f}%)\n\n"
            )

        f.write("## 次のデータ強化ポイント\n")
        f.write("- 各レイヤーの公開TAM/SAMデータでシェア仮定を置換。\n")
        f.write("- 2025年以降の推計値を実測公開値へ更新。\n")
        f.write("- 地域別（US/JP/Global）に分割して感度分析を追加。\n")

    print(f"Wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
