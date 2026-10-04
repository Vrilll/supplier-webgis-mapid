# Supplier WebGIS — MAPID × BINUS HomeTask

Svelte 4, Vite 5, and MapLibre GL 4. MAPID basemaps, with 50,000 supplier
points delivered as Mapbox Vector Tiles (MVT).

Based on the class repo
[radenpranantya/webgis-binus-mapid-svelte](https://github.com/radenpranantya/webgis-binus-mapid-svelte).

## HomeTask checklist

| # | Task | Where |
| --- | --- | --- |
| 1 | Replicate today's WebGIS | Same stack and flow as class: 4 basemaps, MVT points from `tiles/server.py`, click popup. `src/lib/config.js`, `src/lib/MapView.svelte`, `src/App.svelte` |
| 2 | Redesign the attribute popup | `src/lib/PopupCard.svelte` (a Svelte component mounted into the MapLibre popup) and popup styles in `src/app.css` |
| 3 | Toggle on/off for the point layer | Switch in the **Layers** panel. `showPoints` in `src/App.svelte`, `syncPoints()` in `src/lib/MapView.svelte` |

### 2. Popup redesign

The class popup was four lines of plain text. The new card:

- Leads with the plot area, the number a supplier analyst looks at first, in hectares and m².
- Places the plot on a rank strip against all 49,989 plots that have an area, with the median marked, and says it in words ("Larger than 66% of plots"). Percentiles come from `data_mvt/farm-location-50k.csv` via `scripts/plot_stats.py`.
- Lists region, country, and the point's coordinates, with a Copy button.
- Highlights the selected point on the map with an amber ring.
- Says when several plots sit at the same spot, so a user knows to zoom in.
- Escapes nothing by hand: Svelte renders text safely, so attribute values cannot inject HTML.

### 3. Layer toggle

- The first time the switch turns on, the vector source is added and tiles load (same as **Use MVT** in class).
- After that the switch only changes the layer's `visibility`. Turning points back on does not download the tiles again.
- The on/off state survives a basemap change: `setStyle(..., { diff: false })` drops custom layers, and `style.load` adds them back with the current visibility.
- Turning points off closes any open popup.
- The switch is a real `role="switch"` button, usable by keyboard and screen reader.

### Other fixes over the class version

- **Popup reuse bug.** Reusing one popup with `closeOnClick: true` means a click on a second point can close the popup it just opened, because MapLibre runs the old close listener after the layer handler. A fresh popup is created per click.
- **Status messages** report a stopped tile server or a missing basemap key instead of showing a blank map.
- **Responsive.** On phones the panel sits at the bottom and starts folded.

## Run locally (same as class)

Needs Node 18+ and Python 3.

```bash
cp .env.example .env          # Windows: copy .env.example .env
# put the class key after VITE_MAPID_KEY=
```

Terminal 1:

```bash
python3 tiles/server.py       # Windows: python tiles/server.py
```

Terminal 2:

```bash
npm install
npm run dev
```

Open http://127.0.0.1:5173/ and switch **Supplier points** on.

## Build for a static host (no Python server)

`tiles/server.py` only runs on a laptop. For hosting, the MBTiles file is exported
to plain files, one per tile, and served next to the page.

```bash
npm run tiles:export          # Windows: npm run tiles:export:win
npm run build
```

`dist/` now holds the page plus `tiles/suppliers/{z}/{x}/{y}.pbf` (14,482 tiles,
about 23 MB). Upload the contents of `dist/` to any static host.
`dist/.htaccess` makes Apache/cPanel answer empty squares with 204, like `server.py`.

## Files

| File | Job |
| --- | --- |
| `src/lib/config.js` | Basemap URLs, tile URL (local server in dev, static files in build), map center and zoom |
| `src/lib/MapView.svelte` | Map, basemap switch, supplier layers, toggle, click, popup |
| `src/lib/PopupCard.svelte` | Attribute card shown in the popup |
| `src/lib/plotStats.js` | Plot area percentiles (generated) |
| `src/App.svelte` | Side panel: layer switch, basemap picker, status |
| `tiles/server.py` | Class tile server, unchanged |
| `scripts/export_tiles.py` | MBTiles to static `.pbf` files |
| `scripts/plot_stats.py` | Rebuilds `plotStats.js` from the CSV |
| `public/.htaccess` | Apache rules for the static build |

## A note on the key

`VITE_*` values are compiled into the JavaScript bundle, so the MAPID key is
readable by anyone who opens the deployed site. That is normal for browser
basemap keys, but the key should be restricted to the site's domain in the
MAPID dashboard if that option exists. `.env` is not committed.
