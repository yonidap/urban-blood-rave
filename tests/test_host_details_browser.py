import os
import sys
import threading
import time
from pathlib import Path

import uvicorn
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DEPLOYED = ROOT / "deployed"
sys.path.insert(0, str(DEPLOYED))
os.environ.setdefault("HOST_KEY", "ci-host-key")

import app as game  # noqa: E402

PORT = 8766
BASE = f"http://127.0.0.1:{PORT}"
KEY = "ci-host-key"


def start_server():
    config = uvicorn.Config(game.app, host="127.0.0.1", port=PORT, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.time() + 10
    import urllib.request
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{BASE}/health", timeout=0.5) as r:
                if r.status == 200:
                    return server, thread
        except Exception:
            time.sleep(0.1)
    raise RuntimeError("Local audit server did not start")


def main():
    server, thread = start_server()
    errors = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.on("pageerror", lambda exc: errors.append(str(exc)))
            page.goto(f"{BASE}/host?key={KEY}", wait_until="domcontentloaded", timeout=15000)

            roster = page.evaluate(
                """async ({key}) => {
                    const r = await fetch('/api/host/state?key=' + encodeURIComponent(key));
                    if (!r.ok) throw new Error('host state ' + r.status);
                    const s = await r.json();
                    return s.players.map(p => ({id:p.id, name:p.name, protected:p.protected}));
                }""",
                {"key": KEY},
            )
            assert len(roster) == 12, roster
            assert all(row["id"] != "yakir" and row["name"] != "Yakir" for row in roster), roster
            assert {row["id"] for row in roster if row["protected"]} == {"gal", "tal", "uri"}, roster

            game_summary = page.locator("summary", has_text="GAME STATE · SPOILERS")
            manual_summary = page.locator("summary", has_text="ADVANCED MANUAL OVERRIDES")
            game_summary.wait_for(timeout=10000)
            manual_summary.wait_for(timeout=10000)

            game_summary.click()
            manual_summary.click()

            assert page.locator("details", has=game_summary).evaluate("el => el.open") is True
            assert page.locator("details", has=manual_summary).evaluate("el => el.open") is True

            # Force the same readiness refresh that previously rebuilt the Host
            # DOM and immediately collapsed both <details> sections.
            page.evaluate("refreshReadiness()")
            page.wait_for_timeout(500)

            game_open = page.locator("details", has=page.locator("summary", has_text="GAME STATE · SPOILERS")).evaluate("el => el.open")
            manual_open = page.locator("details", has=page.locator("summary", has_text="ADVANCED MANUAL OVERRIDES")).evaluate("el => el.open")
            assert game_open is True, "Game State collapsed after live refresh"
            assert manual_open is True, "Advanced Manual Overrides collapsed after live refresh"

            # Also survive the normal periodic readiness refresh.
            page.wait_for_timeout(5500)
            game_open = page.locator("details", has=page.locator("summary", has_text="GAME STATE · SPOILERS")).evaluate("el => el.open")
            manual_open = page.locator("details", has=page.locator("summary", has_text="ADVANCED MANUAL OVERRIDES")).evaluate("el => el.open")
            assert game_open is True, "Game State collapsed after periodic refresh"
            assert manual_open is True, "Advanced Manual Overrides collapsed after periodic refresh"
            assert not errors, f"Browser page errors: {errors}"

            print("Host audit PASS: 12 players, Yakir absent, 3 protected, details persist")
            browser.close()
    finally:
        server.should_exit = True
        thread.join(timeout=5)


if __name__ == "__main__":
    main()
