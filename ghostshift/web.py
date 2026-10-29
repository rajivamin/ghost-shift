"""A local-only interface for Ghost Shift (Python standard library)."""
from __future__ import annotations

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .engine import ROOT, catalog, kill_agent, public_run, read_run, resume_agent, start_run

STATIC = Path(__file__).resolve().parent / "static"

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def _json(self, status: int, obj: dict | list) -> None:
        encoded = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/scenarios":
            return self._json(200, catalog())
        if path.startswith("/api/runs/"):
            try:
                return self._json(200, public_run(read_run(path.split("/")[-1])))
            except (ValueError, FileNotFoundError):
                return self._json(404, {"error": "Run not found"})
        if path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path not in ("/api/start", "/api/terminate", "/api/resume"):
            return self._json(404, {"error": "Unknown endpoint"})
        # Require expected JSON requests from local UI only; disallow cross-origin browser posts.
        origin = self.headers.get("Origin", "")
        if origin and origin not in ("http://127.0.0.1:8765", "http://localhost:8765"):
            return self._json(403, {"error": "Cross-origin request rejected"})
        if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
            return self._json(415, {"error": "Expected application/json"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size <= 0 or size > 4000:
                return self._json(413, {"error": "Invalid request size"})
            body = json.loads(self.rfile.read(size))
            if not isinstance(body, dict):
                raise ValueError("Expected JSON object")
            if path == "/api/start":
                run = start_run(body.get("scenario", ""), body.get("mode", "preview"), body.get("model", "qwen2.5:1.5b"))
            elif path == "/api/terminate":
                run = kill_agent(body.get("run_id", ""))
            else:
                run = resume_agent(body.get("run_id", ""))
            return self._json(200, public_run(run))
        except (ValueError, KeyError, TypeError) as exc:
            return self._json(400, {"error": str(exc)})
        except RuntimeError as exc:
            return self._json(503, {"error": str(exc)})
        except Exception as exc:
            print("Internal error:", repr(exc))
            return self._json(500, {"error": "An unexpected error occurred; see local terminal"})


def main() -> None:
    print("\nGHOST SHIFT | http://127.0.0.1:8765")
    print("Local only. The scripted preview is NOT an AI run.")
    print("Press Ctrl+C to stop.\n")
    with ThreadingHTTPServer(("127.0.0.1", 8765), Handler) as server:
        server.serve_forever()

if __name__ == "__main__":
    main()
