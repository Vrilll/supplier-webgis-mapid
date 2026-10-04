"""Regenerate src/lib/plotStats.js (percentiles of plot area) from the CSV."""
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rows = list(csv.DictReader(open(ROOT / "data_mvt/farm-location-50k.csv", encoding="utf-8")))
v = sorted(float(r["plotareaha"]) for r in rows if r["plotareaha"])
n = len(v)
q = [round(v[min(n - 1, int(i / 100 * (n - 1)))], 2) for i in range(101)]
(ROOT / "src/lib/plotStats.js").write_text(
    "// Generated from data_mvt/farm-location-50k.csv by scripts/plot_stats.py\n"
    f"export const SUPPLIER_COUNT = {len(rows)};\nexport const PLOT_COUNT = {n};\nexport const PLOT_MEDIAN_HA = {v[n // 2]};\n"
    f"export const PLOT_PERCENTILES = {json.dumps(q)};\n"
)
print(f"{n} plots, median {v[n // 2]} ha")
