import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from features import api
from objects.errors import ApiError
from objects.firebase import FIREBASE_CONFIG

HOST = "127.0.0.1"
PORT = 8765


class CalendarHandler(BaseHTTPRequestHandler):
    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, status: int, payload) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self._cors()
        self.end_headers()
        self.wfile.write(raw)

    def _empty(self) -> None:
        self.send_response(204)
        self._cors()
        self.end_headers()

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ApiError(400, "Invalid JSON") from exc

    def do_OPTIONS(self) -> None:
        self._empty()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        qs = api.parse_query(parsed.query)
        try:
            if parsed.path == "/api/calendar":
                self._json(200, api.get_calendar(qs))
            elif parsed.path == "/api/calendar/preMonth":
                self._json(200, api.get_pre_month(qs))
            elif parsed.path == "/api/calendar/nextMonth":
                self._json(200, api.get_next_month(qs))
            elif parsed.path == "/api/calendar/search":
                self._json(200, api.search_date(qs))
            elif parsed.path == "/api/memos":
                self._json(200, api.list_memos(qs))
            else:
                self._json(404, {"detail": "Not found"})
        except ApiError as exc:
            self._json(exc.status, {"detail": exc.detail})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/memos":
                self._json(201, api.create_memo(self._read_json()))
            else:
                self._json(404, {"detail": "Not found"})
        except ApiError as exc:
            self._json(exc.status, {"detail": exc.detail})

    def do_PUT(self) -> None:
        parsed = urlparse(self.path)
        try:
            memo_id = memo_id_from_path(parsed.path)
            if memo_id is None:
                self._json(404, {"detail": "Not found"})
                return
            self._json(200, api.update_memo(memo_id, self._read_json()))
        except ApiError as exc:
            self._json(exc.status, {"detail": exc.detail})

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        try:
            memo_id = memo_id_from_path(parsed.path)
            if memo_id is None:
                self._json(404, {"detail": "Not found"})
                return
            api.delete_memo(memo_id)
            self._empty()
        except ApiError as exc:
            self._json(exc.status, {"detail": exc.detail})

    def log_message(self, fmt: str, *args) -> None:
        print("%s - %s" % (self.address_string(), fmt % args))


def memo_id_from_path(path: str) -> int | None:
    prefix = "/api/memos/"
    if not path.startswith(prefix):
        return None
    rest = path[len(prefix) :]
    if not rest.isdigit():
        return None
    return int(rest)


def main() -> None:
    print(f"Firebase project: {FIREBASE_CONFIG['projectId']}")
    print(f"Firebase databaseURL: {FIREBASE_CONFIG['databaseURL']}")
    server = ThreadingHTTPServer((HOST, PORT), CalendarHandler)
    print(f"Calendar backend listening on http://{HOST}:{PORT}")
    server.serve_forever()
