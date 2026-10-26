from pathlib import Path
import base64
import gzip
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
OVERLAY_PARTS = [
    ROOT / "overlay_v226" / "part1.b64",
    ROOT / "overlay_v226" / "part2.b64",
    ROOT / "overlay_v226" / "part3a.b64",
    ROOT / "overlay_v226" / "part3b.b64",
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

# v2.26 Web Push / iPhone PWA upgrade.
missing_overlay = [str(p) for p in OVERLAY_PARTS if not p.exists()]
if missing_overlay:
    raise SystemExit(f"Missing v2.26 overlay parts: {missing_overlay}")

overlay_payload = "".join(
    p.read_text(encoding="utf-8").strip() for p in OVERLAY_PARTS
)
overlay_archive = base64.b64decode(overlay_payload, validate=True)
with tarfile.open(fileobj=io.BytesIO(overlay_archive), mode="r:gz") as tf:
    tf.extractall(target)

# v2.26.1 iPhone layout/alerts hotfix.
# iOS standalone PWAs were leaving a white strip at the bottom, clipping the
# alert footer, and the translucent status bar blurred the logo/timer area.
player = target / "public" / "player.html"
html = player.read_text(encoding="utf-8")

patches = [
    (
        '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">',
        '<meta name="apple-mobile-web-app-status-bar-style" content="black">',
    ),
    (
        '    html,body{height:100%;overflow:hidden}\n'
        '    body{background:\n'
        '      radial-gradient(circle at 50% -10%,rgba(209,10,44,.18),transparent 35%),\n'
        '      radial-gradient(circle at 10% 110%,rgba(91,7,23,.16),transparent 40%),\n'
        '      linear-gradient(180deg,#12050b 0%,#060609 50%,#020203 100%)}\n'
        '    .game{height:100dvh;min-height:100vh;display:grid;grid-template-rows:auto 1fr auto;padding:max(18px,env(safe-area-inset-top)) 20px max(18px,env(safe-area-inset-bottom));position:relative;overflow:hidden}\n',
        '    html{width:100%;height:100%;background:#020203;overflow:hidden}\n'
        '    body{margin:0;width:100%;height:100%;min-height:100%;overflow:hidden;background:#020203}\n'
        '    .game{position:fixed;inset:0;width:100%;height:100svh;height:100dvh;box-sizing:border-box;display:grid;grid-template-rows:auto minmax(0,1fr) auto;padding:calc(env(safe-area-inset-top) + 14px) 20px calc(env(safe-area-inset-bottom) + 12px);overflow:hidden;background:\n'
        '      radial-gradient(circle at 50% -10%,rgba(209,10,44,.18),transparent 35%),\n'
        '      radial-gradient(circle at 10% 110%,rgba(91,7,23,.16),transparent 40%),\n'
        '      linear-gradient(180deg,#12050b 0%,#060609 50%,#020203 100%);transform:translateZ(0)}\n',
    ),
    (
        '    .topbar{display:flex;align-items:flex-start;justify-content:space-between;gap:18px}\n',
        '    .topbar{display:flex;align-items:flex-start;justify-content:space-between;gap:18px;transform:none;filter:none;-webkit-filter:none;backdrop-filter:none;-webkit-backdrop-filter:none}\n',
    ),
    (
        '    .footer{display:flex;justify-content:center;align-items:center;min-height:34px}\n'
        '    #alertSetup{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:#c9bac1}\n',
        '    .footer{display:flex;justify-content:center;align-items:center;min-height:42px;padding-top:4px;position:relative;z-index:5}\n'
        '    #alertSetup{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:#c9bac1;min-height:24px;display:flex;align-items:center;justify-content:center;text-align:center}\n',
    ),
    (
        "function renderAlertSetup(){\n"
        "  if(isIos()&&!isStandalone()){alertSetup.innerHTML='<span>Add to Home Screen to enable alerts</span>';return}\n"
        "  if(!('serviceWorker'in navigator)||!('PushManager'in window)||!('Notification'in window)){alertSetup.innerHTML='<span>Action alerts unavailable</span>';return}\n"
        "  if(Notification.permission==='denied'){alertSetup.innerHTML='<span>Alerts blocked in Settings</span>';return}\n"
        "  if(pushSubscribed){alertSetup.innerHTML='<span>ACTION ALERTS ON</span>';return}\n"
        "  if(!pushReady){alertSetup.innerHTML='<span>Preparing alerts…</span>';return}\n"
        "  alertSetup.innerHTML=`<button class=\"notify-btn\" onclick=\"enableAlerts()\">Enable action alerts</button>`\n"
        "}\n",
        "function renderAlertSetup(){\n"
        "  if(isIos()&&!isStandalone()){alertSetup.innerHTML='<span>Add to Home Screen to enable alerts</span>';return}\n"
        "  const hasPushApis=('serviceWorker'in navigator)&&('PushManager'in window)&&('Notification'in window);\n"
        "  if(!hasPushApis){alertSetup.innerHTML='<span>Action alerts unavailable on this device</span>';return}\n"
        "  if(Notification.permission==='denied'){alertSetup.innerHTML='<span>Alerts blocked in Settings</span>';return}\n"
        "  if(pushSubscribed){alertSetup.innerHTML='<span>ACTION ALERTS ON</span>';return}\n"
        "  alertSetup.innerHTML=`<button class=\"notify-btn\" onclick=\"enableAlerts()\">Enable action alerts</button>`\n"
        "}\n",
    ),
    (
        'preparePush();\n</script>',
        'renderAlertSetup();\npreparePush();\n</script>',
    ),
]

for old, new in patches:
    if old not in html:
        raise SystemExit("v2.26.1 mobile hotfix could not find an expected player.html fragment")
    html = html.replace(old, new, 1)

player.write_text(html, encoding="utf-8")

# v2.27 reveal hotfix: remove the synthetic flame video entirely and replace
# the public vote reveal with a cinematic burn/dissolve + embers treatment.
screen_hotfix = ROOT / "screen_v227.b64"
if not screen_hotfix.exists():
    raise SystemExit("Missing v2.27 screen reveal hotfix")
screen_bytes = gzip.decompress(base64.b64decode(screen_hotfix.read_text(encoding="utf-8").strip(), validate=True))
(target / "public" / "screen.html").write_bytes(screen_bytes)

required = [
    target / "app.py",
    target / "requirements.txt",
    target / "public" / "screen.html",
    target / "public" / "player.html",
    target / "public" / "host.html",
    target / "public" / "fire_overlay.webm",
    target / "public" / "sw.js",
    target / "public" / "manifest.webmanifest",
    target / "public" / "icon-180.png",
    target / "public" / "icon-512.png",
]
missing_required = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
if missing_required:
    raise SystemExit(f"Deployment bundle is incomplete: {missing_required}")

print("Urban Blood Rave deployment bundle extracted successfully (v2.27 cinematic reveal applied).")
