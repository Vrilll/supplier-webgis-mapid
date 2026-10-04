const MAPID_KEY = import.meta.env.VITE_MAPID_KEY;

export const basemaps = {
  street: `https://basemap.mapid.io/styles/street-2d-building/style.json?key=${MAPID_KEY}`,
  light: `https://basemap.mapid.io/styles/light/style.json?key=${MAPID_KEY}`,
  satellite: `https://basemap.mapid.io/styles/satellite/style.json?key=${MAPID_KEY}`,
  demo: 'https://demotiles.maplibre.org/style.json'
};

// Dev (npm run dev): tiles come from the Python server, exactly like in class.
// Build (npm run build): tiles are static files in public/tiles, exported by
// scripts/export_tiles.py, so the site runs on any static host.
// Override either with VITE_MVT_TILES in .env (a URL, or the word "static").
const LOCAL_TILES = 'http://127.0.0.1:8080/suppliers/{z}/{x}/{y}.mvt';
const STATIC_TILES = `${import.meta.env.BASE_URL}tiles/suppliers/{z}/{x}/{y}.pbf`;
const tilesEnv = import.meta.env.VITE_MVT_TILES;

function absolute(url) {
  // MapLibre needs an absolute URL; URL() encodes the braces, so put them back.
  return new URL(url, window.location.href).href.replace(/%7B/g, '{').replace(/%7D/g, '}');
}

export const MVT_TILES = absolute(
  tilesEnv === 'static' ? STATIC_TILES : tilesEnv || (import.meta.env.PROD ? STATIC_TILES : LOCAL_TILES)
);
export const MVT_SOURCE_LAYER = 'suppliers';
export const MAP_CENTER = [-7.7, 7.2];
export const MAP_ZOOM = 9;
