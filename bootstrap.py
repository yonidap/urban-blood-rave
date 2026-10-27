from pathlib import Path
import base64
import gzip
import io
import runpy
import shutil
import tarfile

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "deployed"
BUILD = "v2.37"

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


def run_hotfix(filename: str):
    path = ROOT / filename
    if not path.exists():
        raise SystemExit(f"Missing {filename}")
    runpy.run_path(str(path), run_name="__main__")


if TARGET.exists():
    shutil.rmtree(TARGET)
TARGET.mkdir(parents=True)

# Base application + Web Push/PWA overlay.
extract_b64_tar(BASE_PARTS, "base deployment bundle")
extract_b64_tar(OVERLAY_PARTS, "v2.26 overlay")

# Server/player fixes.
run_hotfix("game_flow_hotfix.py")
run_hotfix("player_hotfix.py")
run_hotfix("push_reliability_hotfix.py")
run_hotfix("push_privacy_hotfix.py")

# Main-screen reveal baseline.
screen_hotfix = ROOT / "screen_v227.b64"
if not screen_hotfix.exists():
    raise SystemExit("Missing v2.27 screen reveal hotfix")
screen_bytes = gzip.decompress(
    base64.b64decode(screen_hotfix.read_text(encoding="utf-8").strip(), validate=True)
)
(TARGET / "public" / "screen.html").write_bytes(screen_bytes)

# Public-display transition baseline, then splash-then-drip pass.
run_hotfix("screen_glitch_hotfix.py")
run_hotfix("blood_splash_hotfix.py")
run_hotfix("screen_runtime_hotfix.py")

# Static build marker lets an already-open /screen detect a newer deploy.
(TARGET / "public" / "build.txt").write_text(BUILD + "\n", encoding="utf-8")

required = [
    TARGET / "app.py",
    TARGET / "requirements.txt",
    TARGET / "public" / "screen.html",
    TARGET / "public" / "player.html",
    TARGET / "public" / "host.html",
    TARGET / "public" / "sw.js",
    TARGET / "public" / "manifest.webmanifest",
    TARGET / "public" / "build.txt",
]
missing_required = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
if missing_required:
    raise SystemExit(f"Deployment bundle is incomplete: {missing_required}")

print(f"Urban Blood Rave deployment built successfully ({BUILD}).")
