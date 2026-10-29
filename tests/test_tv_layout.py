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

PORT = 8765
BASE = f"http://127.0.0.1:{PORT}"


def prepare_worst_case_tv_state():
    # Static worst-case main screen: all six clues and all four protected
    # portraits visible at once. Do not start the scheduler; this test is about
    # production DOM/CSS geometry, not game time.
    game.state["status"] = "running"
    game.state["phase"] = "running"
    game.state["elapsedSec"] = 2400
    game.state["activeClueIndex"] = None
    game.state["activeClueUntil"] = None
    game.state["reveal"] = None
    game.state["revealQueue"] = []
    game.state["votesOpen"] = False
    game.state["discussionEndsAt"] = None
    game.state["activeBiteWindow"] = None
    game.state["publishedClues"] = list(range(6))

    protected = [p for p in game.state["players"] if p.get("protected")]
    for p in protected:
        p["scarred"] = True
    game.state["scarLoop"] = [
        {"playerId": p["id"], "name": p["name"], "video": p.get("scarVideo")}
        for p in protected
    ]


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
    prepare_worst_case_tv_state()
    server, thread = start_server()
    errors = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1920, "height": 1080})
            page.on("pageerror", lambda exc: errors.append(str(exc)))
            page.goto(f"{BASE}/screen?debug=1", wait_until="domcontentloaded", timeout=15000)
            page.wait_for_function("document.querySelectorAll('.clue-row').length === 6", timeout=10000)
            page.wait_for_function("document.querySelectorAll('.scar-person').length === 4", timeout=10000)
            page.wait_for_timeout(1200)

            result = page.evaluate("""
                () => {
                  const visible = el => {
                    const s = getComputedStyle(el);
                    const r = el.getBoundingClientRect();
                    return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;
                  };
                  const boxes = selectors => selectors.flatMap(sel =>
                    [...document.querySelectorAll(sel)].filter(visible).map(el => {
                      const r = el.getBoundingClientRect();
                      return {sel, left:r.left, top:r.top, right:r.right, bottom:r.bottom, width:r.width, height:r.height};
                    })
                  );
                  const important = boxes([
                    '.main', '.bottom-zone', '.clues', '.clue-row',
                    '.scar-gallery', '.scar-person', '.topbar', '.stats'
                  ]);
                  const offenders = important.filter(b =>
                    b.left < -2 || b.top < -2 || b.right > innerWidth + 2 || b.bottom > innerHeight + 2
                  );
                  return {
                    width: innerWidth,
                    height: innerHeight,
                    clueCount: document.querySelectorAll('.clue-row').length,
                    scarCount: document.querySelectorAll('.scar-person').length,
                    scrollWidth: document.documentElement.scrollWidth,
                    scrollHeight: document.documentElement.scrollHeight,
                    bodyScrollWidth: document.body.scrollWidth,
                    bodyScrollHeight: document.body.scrollHeight,
                    offenders,
                    build: document.documentElement.dataset.ubrBuild || null,
                  };
                }
            """)

            assert result["build"] == "v2.47", result
            assert result["clueCount"] == 6, result
            assert result["scarCount"] == 4, result
            assert result["scrollWidth"] <= 1922, result
            assert result["bodyScrollWidth"] <= 1922, result
            assert not result["offenders"], result
            # The page intentionally uses overflow:hidden, so scrollHeight can
            # be equal to viewport. A >2 px excess is a genuine clipped layout.
            assert result["scrollHeight"] <= 1082, result
            assert result["bodyScrollHeight"] <= 1082, result
            assert not errors, f"Browser page errors: {errors}"

            print("TV worst-case layout PASS:", result)
            browser.close()
    finally:
        server.should_exit = True
        thread.join(timeout=5)


if __name__ == "__main__":
    main()
