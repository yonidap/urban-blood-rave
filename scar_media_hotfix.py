from pathlib import Path

ROOT = Path(__file__).resolve().parent
app_path = ROOT / "deployed" / "app.py"
app = app_path.read_text(encoding="utf-8")

old = "dict(id='uri', name='Ori', token="
if old not in app:
    raise SystemExit("scar media hotfix: Ori player anchor not found")

if "scarVideo='/scars/uri.mp4'" in app:
    app = app.replace("scarVideo='/scars/uri.mp4'", "scarVideo='/scars/ori.mp4'", 1)
elif "scarVideo='/scars/ori.mp4'" not in app:
    raise SystemExit("scar media hotfix: Ori scarVideo mapping not found")

for path in ["/scars/gal.mp4", "/scars/yakir.mp4", "/scars/tal.mp4", "/scars/ori.mp4"]:
    if path not in app:
        raise SystemExit(f"scar media hotfix: missing app mapping {path}")

app_path.write_text(app, encoding="utf-8")
print("Applied protected-player scar media mapping (Gal/Yakir/Tal/Ori).")
