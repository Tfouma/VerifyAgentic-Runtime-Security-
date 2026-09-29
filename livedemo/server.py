"""Local web server for the live demo.

    python3 -m livedemo                # http://127.0.0.1:8765
    python3 -m livedemo --port 9000 --rythme 2.0

Serves the console (ui.html), the gateway endpoints the agents call, and a
small JSON API for the console. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import threading
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .agents import SCENARIOS
from .core import POLICY_FILE, World
from .gateway import Gateway

UI = Path(__file__).parent / "ui.html"


class App:
    def __init__(self, pace: float):
        self.pace = pace
        self.base = ""
        self.lock = threading.Lock()
        self.reset()

    def reset(self):
        step = getattr(self, "world", None) and self.world.step_mode
        if getattr(self, "world", None):
            self.world.release_step()   # free an agent parked on the old world
        self.world = World()
        self.world.step_mode = bool(step)
        self.gateway = Gateway(self.world)
        self.running: str | None = None

    def run(self, name: str) -> dict:
        if name not in SCENARIOS:
            return {"ok": False, "erreur": "scénario inconnu"}
        with self.lock:
            if self.running:
                return {"ok": False, "erreur": f"scénario « {self.running} » en cours"}
            if not self.world.user_token or not self.world.entra.active_session():
                return {"ok": False, "erreur": "connectez-vous d'abord avec Entra ID"}
            self.running = name
        world = self.world

        def go():
            try:
                SCENARIOS[name](world, self.base, self.pace)
            except Exception as exc:  # noqa: BLE001 - surface anything to the console
                world.bus.emit("deny", "Erreur du scénario", f"{exc}\n{traceback.format_exc(limit=2)}", src="démo")
            finally:
                if self.world is world:
                    self.running = None

        threading.Thread(target=go, daemon=True).start()
        return {"ok": True}


def make_handler(app: App):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):  # quiet
            pass

        def _send(self, code: int, body, ctype="application/json; charset=utf-8"):
            data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _body(self) -> dict:
            n = int(self.headers.get("Content-Length") or 0)
            return json.loads(self.rfile.read(n) or b"{}")

        def do_GET(self):
            u = urlparse(self.path)
            w = app.world
            if u.path in ("/", "/index.html"):
                return self._send(200, UI.read_bytes(), "text/html; charset=utf-8")
            if u.path == "/api/state":
                return self._send(200, {**w.state(), "en_cours": app.running})
            if u.path == "/api/events":
                after = int(parse_qs(u.query).get("after", ["0"])[0])
                return self._send(200, w.bus.since(after))
            if u.path == "/api/politique":
                return self._send(200, json.loads(POLICY_FILE.read_text(encoding="utf-8")))
            if u.path == "/gateway/tools":
                return self._send(200, app.gateway.tools())
            self._send(404, {"erreur": "introuvable"})

        def do_POST(self):
            u = urlparse(self.path)
            body = self._body()
            w = app.world
            if u.path == "/api/login":
                w.user_token = w.entra.login()
                return self._send(200, {"ok": True})
            if u.path == "/api/run":
                return self._send(200, app.run(body.get("scenario", "")))
            if u.path == "/api/approve":
                ch = w.verify.pending_challenge()
                if not ch:
                    return self._send(200, {"ok": False, "status": "aucune demande"})
                return self._send(200, w.verify.answer(ch.id, str(body.get("code", ""))))
            if u.path == "/api/restore":
                w.verify.restore(body.get("agent", "agent-csc-parent"))
                w.refused.clear()
                return self._send(200, {"ok": True})
            if u.path == "/api/pas-a-pas":
                w.step_mode = bool(body.get("actif"))
                if not w.step_mode:
                    w.release_step()
                return self._send(200, {"ok": True, "actif": w.step_mode})
            if u.path == "/api/etape":
                w.release_step()
                return self._send(200, {"ok": True})
            if u.path == "/api/reset":
                app.reset()
                return self._send(200, {"ok": True})
            if u.path == "/gateway/mcp":
                return self._send(200, app.gateway.call(body))
            if u.path == "/gateway/delegate":
                return self._send(200, app.gateway.delegate(body))
            self._send(404, {"erreur": "introuvable"})

    return Handler


def serve(port: int = 8765, pace: float = 1.4, open_browser: bool = False) -> ThreadingHTTPServer:
    app = App(pace)
    httpd = ThreadingHTTPServer(("127.0.0.1", port), make_handler(app))
    httpd.daemon_threads = True
    app.base = f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.app = app
    if open_browser:
        webbrowser.open(app.base)
    return httpd


def main():
    ap = argparse.ArgumentParser(description="Démo en direct : agent gouverné en bac à sable")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--rythme", type=float, default=1.4, help="pause (s) entre les étapes de l'agent")
    ap.add_argument("--ouvrir", action="store_true", help="ouvrir le navigateur")
    ap.add_argument("--pas-a-pas", action="store_true", help="démarrer en mode pas à pas")
    a = ap.parse_args()
    httpd = serve(a.port, a.rythme, a.ouvrir)
    httpd.app.world.step_mode = a.pas_a_pas
    print(f"Démo prête : {httpd.app.base}   (Ctrl+C pour arrêter)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
