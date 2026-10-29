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
    "maybe_finalize_bite_window",
    "resolve_bite_after_delay",
    "check_early_win",
    "finish_game",
    "api_start",
    "api_reset",
    "api_resolve_vote",
    "api_clue",
    "api_bite_window",
    "api_discussion",
    "api_vote_open",
    "bite",
    "vote",
    "api_host_state",
    "me",
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
for p in game.state["players"]:
    print({k: p.get(k) for k in ("id","name","initialRole","currentRole","protected","token","scarVideo","alive","bitesRemaining","failedBites")})

print("\n=== SCHEDULE ===")
print(getattr(game, "SCHEDULE", None))
print("GAME_DURATION_SEC", getattr(game, "GAME_DURATION_SEC", None))
print("BITE_WINDOW_SEC", getattr(game, "BITE_WINDOW_SEC", None))
print("VOTE_DURATION_SEC", getattr(game, "VOTE_DURATION_SEC", None))
print("DISCUSSION_DURATION_SEC", getattr(game, "DISCUSSION_DURATION_SEC", None))
