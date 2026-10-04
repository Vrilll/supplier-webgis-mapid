"""Export data_mvt/suppliers.mbtiles to static files for hosting without a tile server.

Output: public/tiles/suppliers/{z}/{x}/{y}.pbf  (XYZ scheme, uncompressed)
Vite copies public/ into dist/ on `npm run build`, so any static host
(cPanel, Netlify, Vercel, GitHub Pages) can serve the points.
"""
import gzip, shutil, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MBTILES = ROOT / "data_mvt" / "suppliers.mbtiles"
OUT = ROOT / "public" / "tiles" / "suppliers"

if OUT.exists():
    shutil.rmtree(OUT)

con = sqlite3.connect(f"file:{MBTILES}?mode=ro", uri=True)
count = 0
for z, x, tms_y, data in con.execute("SELECT zoom_level, tile_column, tile_row, tile_data FROM tiles"):
    y = (1 << z) - 1 - tms_y  # MBTiles stores TMS rows; the web uses XYZ
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    path = OUT / str(z) / str(x) / f"{y}.pbf"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    count += 1
con.close()
print(f"Exported {count} tiles to {OUT.relative_to(ROOT)}")
