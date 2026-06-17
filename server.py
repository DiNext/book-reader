#!/usr/bin/env python3
"""Tiny local-network markdown book reader.

Serves the chapters in BOOK_DIR over your LAN so you can read them on your
phone's browser. Zero dependencies — standard library only.

Usage:  python3 server.py [port]
"""
import json
import os
import socket
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

BOOK_DIR = "/Users/dmitryalexeenko/Desktop/dev/kingdom-story/story"
HERE = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080


def list_files():
    """Return every .md file under BOOK_DIR as relative posix paths, sorted."""
    out = []
    for root, _dirs, files in os.walk(BOOK_DIR):
        for f in sorted(files):
            if f.endswith(".md"):
                rel = os.path.relpath(os.path.join(root, f), BOOK_DIR)
                out.append(rel.replace(os.sep, "/"))
    out.sort()
    return out


def safe_path(rel):
    """Resolve a client-supplied relative path, blocking traversal escapes."""
    full = os.path.normpath(os.path.join(BOOK_DIR, rel))
    if not full.startswith(os.path.abspath(BOOK_DIR) + os.sep) and full != os.path.abspath(BOOK_DIR):
        return None
    return full


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path, ctype):
        try:
            with open(path, "rb") as fh:
                self._send(200, fh.read(), ctype)
        except FileNotFoundError:
            self._send(404, "not found", "text/plain")

    def do_GET(self):
        u = urlparse(self.path)
        route = u.path

        if route == "/" or route == "/index.html":
            return self._send_file(os.path.join(HERE, "index.html"), "text/html; charset=utf-8")

        if route == "/vendor/marked.min.js":
            return self._send_file(os.path.join(HERE, "vendor", "marked.min.js"),
                                   "application/javascript; charset=utf-8")

        if route == "/api/files":
            return self._send(200, json.dumps(list_files()))

        if route == "/api/file":
            rel = unquote(parse_qs(u.query).get("path", [""])[0])
            full = safe_path(rel)
            if not full or not os.path.isfile(full):
                return self._send(404, json.dumps({"error": "not found"}))
            with open(full, "r", encoding="utf-8") as fh:
                return self._send(200, fh.read(), "text/markdown; charset=utf-8")

        return self._send(404, "not found", "text/plain")

    def do_PUT(self):
        u = urlparse(self.path)
        if u.path == "/api/file":
            rel = unquote(parse_qs(u.query).get("path", [""])[0])
            full = safe_path(rel)
            if not full or not os.path.isfile(full):
                return self._send(404, json.dumps({"error": "not found"}))
            length = int(self.headers.get("Content-Length", 0) or 0)
            data = self.rfile.read(length).decode("utf-8")
            with open(full, "w", encoding="utf-8") as fh:
                fh.write(data)
            return self._send(200, json.dumps({"ok": True}))

        return self._send(404, "not found", "text/plain")

    def log_message(self, *args):
        pass  # quiet


def lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


if __name__ == "__main__":
    if not os.path.isdir(BOOK_DIR):
        print(f"Book folder not found: {BOOK_DIR}")
        sys.exit(1)
    srv = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    ip = lan_ip()
    print("📖 Book reader running")
    print(f"   On this Mac:  http://localhost:{PORT}")
    print(f"   On your phone: http://{ip}:{PORT}   (same Wi-Fi)")
    print("   Press Ctrl+C to stop.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")
