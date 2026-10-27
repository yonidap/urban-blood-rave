from pathlib import Path
import base64
import gzip
import io
import runpy
import shutil
import tarfile

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "deployed"

BASE_PARTS = [
    ROOT / "deploy_bundle" / "bundle.part01",
    ROOT / "deploy_bundle" / "part2a.b64",
    ROOT / "deploy_bundle" / "part2b.b64",
    ROOT / "deploy_bundle" / "part3a.b64",
    ROOT / "deploy_bundle" / "part3b.b64",
    ROOT / "deploy_bundle" / "part4a.b64",
    ROOT / "deploy_bundle" / "part4b.b64",
]

OVERLAY_PARTS = [
    ROOT / "overlay_v226" / "part1.b64",
    ROOT / "overlay_v226" / "part2.b64",
    ROOT / "overlay_v226" / "part3a.b64",
    ROOT / "overlay_v226" / "part3b.b64",
]


def extract_b64_tar(parts, label: str):
    missing = [str(p) for p in parts if not p.exists()]
    if missing:
        raise SystemExit(f"Missing {label} parts: {missing}")
    payload = "".join(p.read_text(encoding="utf-8").strip() for p in parts)
    archive = base64.b64decode(payload, validate=True)
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tf:
        tf.extractall(TARGET)


if TARGET.exists():
    shutil.rmtree(TARGET)
TARGET.mkdir(parents=True)

# v2.25 base application.
extract_b64_tar(BASE_PARTS, "base deployment bundle")

# v2.26 Web Push / PWA upgrade.
extract_b64_tar(OVERLAY_PARTS, "v2.26 overlay")

# Phone-cue flow: decoys wait until a clue takeover is finished and bite
# windows only show CHECK YOUR PHONES when someone can actually act.
game_flow_hotfix = ROOT / "game_flow_hotfix.py"
if not game_flow_hotfix.exists():
    raise SystemExit("Missing game_flow_hotfix.py")
runpy.run_path(str(game_flow_hotfix), run_name="__main__")

# Current player-page fixes.
player_hotfix = ROOT / "player_hotfix.py"
if not player_hotfix.exists():
    raise SystemExit("Missing player_hotfix.py")
runpy.run_path(str(player_hotfix), run_name="__main__")

# v2.27 main-screen vote reveal: cinematic burn/dissolve, no flame video.
screen_hotfix = ROOT / "screen_v227.b64"
if not screen_hotfix.exists():
    raise SystemExit("Missing v2.27 screen reveal hotfix")
screen_bytes = gzip.decompress(
    base64.b64decode(screen_hotfix.read_text(encoding="utf-8").strip(), validate=True)
)
(TARGET / "public" / "screen.html").write_bytes(screen_bytes)

# v2.30 public-display transitions: unmistakable full-viewport signal glitch
# on every actual scene change (clue open/close, vote, reveal, scar, ending, etc.).
screen_glitch_hotfix = ROOT / "screen_glitch_hotfix.py"
if not screen_glitch_hotfix.exists():
    raise SystemExit("Missing screen_glitch_hotfix.py")
runpy.run_path(str(screen_glitch_hotfix), run_name="__main__")

required = [
    TARGET / "app.py",
    TARGET / "requirements.txt",
    TARGET / "public" / "screen.html",
    TARGET / "public" / "player.html",
    TARGET / "public" / "host.html",
    TARGET / "public" / "fire_overlay.webm",
    TARGET / "public" / "sw.js",
    TARGET / "public" / "manifest.webmanifest",
    TARGET / "public" / "icon-180.png",
    TARGET / "public" / "icon-512.png",
]
missing_required = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
if missing_required:
    raise SystemExit(f"Deployment bundle is incomplete: {missing_required}")

player_text = (TARGET / "public" / "player.html").read_text(encoding="utf-8")
for marker in (
    "function lobbyScene(){",
    "IDENTITY HIDDEN",
    "Visible for 5 seconds",
    "ACTION ALERTS ON",
):
    if marker not in player_text:
        raise SystemExit(f"Player hotfix validation failed: missing {marker!r}")
if "translateZ(0)" in player_text:
    raise SystemExit("Player hotfix validation failed: iOS GPU rasterization transform still present")

app_text = (TARGET / "app.py").read_text(encoding="utf-8")
for marker in ("decoy-deferred", "pendingDecoyEvents", "bite_cue_recipients"):
    if marker not in app_text:
        raise SystemExit(f"Flow hotfix validation failed: missing {marker!r}")

screen_text = (TARGET / "public" / "screen.html").read_text(encoding="utf-8")
for marker in (
    "v2.30 unmistakable viewport glitch controller",
    "ubr-glitching",
    "ubrViewportIn",
    "transitionRender();",
):
    if marker not in screen_text:
        raise SystemExit(f"Screen glitch validation failed: missing {marker!r}")

print("Urban Blood Rave deployment built successfully: clue-safe cues + v2.30 viewport glitch + current privacy/PWA fixes.")
