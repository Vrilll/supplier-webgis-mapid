import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DATA_MVT = Path(__file__).resolve().parents[1] / "data_mvt"
MBTILES = DATA_MVT / "suppliers.mbtiles"
HOST = "0.0.0.0"
PORT = 8080
TILE_CONTENT_TYPE = "application/vnd.mapbox-vector-tile"


def read_tile(zoom, x, tms_y):
    connection = sqlite3.connect(f"file:{MBTILES}?mode=ro", uri=True)
    try:
        return connection.execute(
            "SELECT tile_data FROM tiles WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?",
            (zoom, x, tms_y),
        ).fetchone()
    finally:
        connection.close()


class TileHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def _send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors()
        self.end_headers()

    def do_HEAD(self):
        self.do_GET(head_only=True)

    def do_GET(self, head_only=False):
        path = self.path.split("?", 1)[0].rstrip("/")
        if path in ("", "/"):
            body = b"Supplier tiles:\nGET /suppliers/{z}/{x}/{y}.mvt\n"
            self._send_bytes(200, "text/plain; charset=utf-8", body, head_only)
            return

        parts = path.strip("/").split("/")
        if len(parts) != 4 or parts[0] != "suppliers" or not parts[3].endswith(".mvt"):
            self.send_error(404)
            return

        try:
            zoom = int(parts[1])
            x = int(parts[2])
            y = int(parts[3][: -len(".mvt")])
        except ValueError:
            self.send_error(400)
            return

        tms_y = (1 << zoom) - 1 - y
        row = read_tile(zoom, x, tms_y)

        if not row:
            self.send_response(204)
            self._send_cors()
            self.end_headers()
            return
        self._send_bytes(200, TILE_CONTENT_TYPE, row[0], head_only)

    def _send_bytes(self, status, content_type, body, head_only):
        self.send_response(status)
        self._send_cors()
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if not head_only:
            self.wfile.write(body)


def main():
    if not MBTILES.exists():
        raise SystemExit(f"Missing {MBTILES}. The tile file is data_mvt/suppliers.mbtiles in the repo.")
    server = ThreadingHTTPServer((HOST, PORT), TileHandler)
    print(f"Tiles on http://127.0.0.1:{PORT}/suppliers/{{z}}/{{x}}/{{y}}.mvt")
    server.serve_forever()


if __name__ == "__main__":
    main()
