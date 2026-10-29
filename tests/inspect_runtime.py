import inspect
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPLOYED = ROOT / "deployed"
sys.path.insert(0, str(DEPLOYED))

os.environ.setdefault("HOST_KEY", "ci-host-key")

import app as game  # noqa: E402

print("=== ROUTES ===")
for route in game.app.routes:
    methods = ",".join(sorted(getattr(route, "methods", []) or []))
    print(f"{methods:16} {getattr(route, 'path', ''):45} {getattr(route, 'name', '')}")

print("\n=== STATE KEYS ===")
print(sorted(game.state.keys()))

print("\n=== CRITICAL FUNCTIONS ===")
for name in [
    "scheduler_loop",
    "open_bite_window",
    "send_decoy_alerts",
    "start_discussion",
    "open_vote",
    "resolve_vote",
    "show_clue",
    "process_bite",
    "check_win_conditions",
    "reset_game",
    "start_game",
]:
    fn = getattr(game, name, None)
    if fn is None:
        print(f"--- {name}: MISSING ---")
        continue
    print(f"\n--- {name} ---")
    try:
        print(inspect.getsource(fn))
    except Exception as exc:
        print(f"SOURCE ERROR: {exc}")

print("\n=== PLAYERS ===")
for p in game.players:
    print({k: p.get(k) for k in ("id","name","initialRole","currentRole","protected","token","scarVideo")})
