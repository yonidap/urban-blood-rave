from pathlib import Path
import base64
import io
import shutil
import tarfile

ROOT = Path(__file__).resolve().parent
PARTS = [
    ROOT / "deploy_bundle" / "bundle.part01",
    ROOT / "deploy_bundle" / "part2a.b64",
    ROOT / "deploy_bundle" / "part2b.b64",
    ROOT / "deploy_bundle" / "part3a.b64",
    ROOT / "deploy_bundle" / "part3b.b64",
    ROOT / "deploy_bundle" / "part4a.b64",
    ROOT / "deploy_bundle" / "part4b.b64",
]

missing = [str(p) for p in PARTS if not p.exists()]
if missing:
    raise SystemExit(f"Missing deployment bundle parts: {missing}")

payload = "".join(p.read_text(encoding="utf-8").strip() for p in PARTS)
archive = base64.b64decode(payload, validate=True)

target = ROOT / "deployed"
if target.exists():
    shutil.rmtree(target)
target.mkdir(parents=True)

with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tf:
    tf.extractall(target)

# v2.26 overlay: Web Push / iPhone PWA support. Keeping this as an overlay
# lets the existing binary asset bundle remain untouched while replacing only
# the files that changed.
overlay_file = ROOT / "overlay_v226.b64"
if overlay_file.exists():
    overlay_archive = base64.b64decode(overlay_file.read_text(encoding="utf-8").strip(), validate=True)
    with tarfile.open(fileobj=io.BytesIO(overlay_archive), mode="r:gz") as tf:
        tf.extractall(target)

required = [
    target / "app.py",
    target / "requirements.txt",
    target / "public" / "screen.html",
    target / "public" / "player.html",
    target / "public" / "host.html",
    target / "public" / "fire_overlay.webm",
    target / "public" / "sw.js",
    target / "public" / "manifest.webmanifest",
]
missing_required = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
if missing_required:
    raise SystemExit(f"Deployment bundle is incomplete: {missing_required}")

print("Urban Blood Rave deployment bundle extracted successfully (v2.26 Web Push overlay applied).")
