from pathlib import Path

ROOT = Path(__file__).resolve().parent
player = ROOT / "deployed" / "public" / "player.html"
html = player.read_text(encoding="utf-8")


def replace_if_present(old: str, new: str) -> None:
    global html
    if new in html:
        return
    if old in html:
        html = html.replace(old, new, 1)


# ---- iPhone/PWA layout fixes ----
replace_if_present(
    '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">',
    '<meta name="apple-mobile-web-app-status-bar-style" content="black">',
)

replace_if_present(
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
    '      linear-gradient(180deg,#12050b 0%,#060609 50%,#020203 100%)}\n',
)

replace_if_present(
    '    .topbar{display:flex;align-items:flex-start;justify-content:space-between;gap:18px}\n',
    '    .topbar{display:flex;align-items:flex-start;justify-content:space-between;gap:18px;transform:none;filter:none;-webkit-filter:none;backdrop-filter:none;-webkit-backdrop-filter:none;-webkit-font-smoothing:antialiased;text-rendering:geometricPrecision}\n',
)

replace_if_present(
    '    .footer{display:flex;justify-content:center;align-items:center;min-height:34px}\n'
    '    #alertSetup{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:#c9bac1}\n',
    '    .footer{display:flex;justify-content:center;align-items:center;min-height:42px;padding-top:4px;position:relative;z-index:5}\n'
    '    #alertSetup{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:#c9bac1;min-height:24px;display:flex;align-items:center;justify-content:center;text-align:center}\n',
)

# Remove GPU promotion of the full page: on iOS this can rasterize the header
# and make the small logo/timer text look smeared.
html = html.replace(';transform:translateZ(0)}', '}')

# Keep the tiny header crisp; the large role title can retain its glow.
html = html.replace(
    '    .logo{font-family:var(--drip);font-size:12px;line-height:1.2;color:#d91535;text-transform:uppercase;text-shadow:0 0 20px rgba(209,10,44,.34)}',
    '    .logo{font-family:var(--drip);font-size:12px;line-height:1.2;color:#d91535;text-transform:uppercase;text-shadow:none;-webkit-font-smoothing:antialiased;text-rendering:geometricPrecision}',
)
html = html.replace(
    '    .sunrise .time{font-family:var(--mono);font-size:24px;font-weight:700;color:#d91535;margin-top:2px}',
    '    .sunrise .time{font-family:var(--mono);font-size:24px;font-weight:700;color:#d91535;margin-top:2px;text-shadow:none;-webkit-font-smoothing:antialiased;text-rendering:geometricPrecision}',
)

# ---- Push-control visibility ----
replace_if_present(
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
)
if 'renderAlertSetup();\npreparePush();\n</script>' not in html and 'preparePush();\n</script>' in html:
    html = html.replace('preparePush();\n</script>', 'renderAlertSetup();\npreparePush();\n</script>', 1)

# ---- Role privacy + pre-game preview ----
if 'function lobbyScene(){' not in html:
    html = html.replace(
        '    .notify-btn{border:0;background:transparent;color:#d5c4cc;font-family:var(--mono);font-size:10px;letter-spacing:.15em;text-transform:uppercase;text-decoration:underline;text-underline-offset:5px;cursor:pointer;padding:8px}\n',
        '    .notify-btn{border:0;background:transparent;color:#d5c4cc;font-family:var(--mono);font-size:10px;letter-spacing:.15em;text-transform:uppercase;text-decoration:underline;text-underline-offset:5px;cursor:pointer;padding:8px}\n'
        '    .identity-hidden{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px;min-height:42dvh}\n'
        '    .identity-hidden .micro{color:#a9959e}\n'
        '    .identity-mask{font-family:var(--ui);font-size:clamp(34px,10vw,56px);font-weight:950;line-height:.95;letter-spacing:-.04em;text-transform:uppercase;color:#544b50}\n'
        '    .role-reveal-btn{margin:4px auto 0;border:1px solid rgba(209,10,44,.48);border-radius:999px;padding:14px 24px;background:rgba(209,10,44,.10);color:#f4e9ee;font-family:var(--mono);font-size:11px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;cursor:pointer}\n'
        '    .role-reveal-btn:active{transform:scale(.985)}\n'
        '    .role-peek-note{font-family:var(--mono);font-size:9px;letter-spacing:.14em;text-transform:uppercase;color:#8f7f86;margin-top:4px}\n'
        '    .preview-role{font-family:var(--ui);font-size:clamp(42px,12vw,72px);font-weight:950;line-height:.9;letter-spacing:-.05em;text-transform:uppercase;margin:0 auto;max-width:900px;color:#fff}\n'
        '    .preview-role.blood{color:#d10a2c;text-shadow:0 0 34px rgba(209,10,44,.28)}\n',
        1,
    )
    html = html.replace(
        "let st,previousState=null,viewMode='main',audioCtx=null,renderPending=false,lastSceneKey=null;\n",
        "let st,previousState=null,viewMode='main',audioCtx=null,renderPending=false,lastSceneKey=null;\nlet secretVisible=false,secretTimer=null;\n",
        1,
    )
    html = html.replace(
        "function roleName(){if(st.initialRole==='original_vampire')return'ORIGINAL VAMPIRE';if(st.currentRole==='converted')return'CONVERTED';return'HUMAN'}\n",
        "function resetSecretVisibility(){secretVisible=false;if(secretTimer){clearTimeout(secretTimer);secretTimer=null}}\n"
        "function hideSecret(){resetSecretVisibility();requestRender(true)}\n"
        "function revealSecret(){resetSecretVisibility();secretVisible=true;requestRender(true);secretTimer=setTimeout(()=>{secretVisible=false;secretTimer=null;requestRender(true)},5000)}\n"
        "document.addEventListener('visibilitychange',()=>{if(document.hidden)resetSecretVisibility()});\n"
        "window.addEventListener('pagehide',resetSecretVisibility);\n"
        "function roleName(){if(st.initialRole==='original_vampire')return'ORIGINAL VAMPIRE';if(st.currentRole==='converted')return'CONVERTED';return'HUMAN'}\n",
        1,
    )
    html = html.replace(
        "  if(prev&&prev.status!==next.status)resetSecretVisibility();\n  st=next;",
        "  if(prev&&prev.status!==next.status)resetSecretVisibility();\n  st=next;",
        1,
    ) if "if(prev&&prev.status!==next.status)resetSecretVisibility();" in html else html.replace(
        "function applyState(next){\n  const prev=previousState;\n  st=next;\n",
        "function applyState(next){\n  const prev=previousState;\n  if(prev&&prev.status!==next.status)resetSecretVisibility();\n  st=next;\n",
        1,
    )
    old_scene = """function idleScene(){
  return `<div class=\"player-name\">${st.name}</div><div class=\"role-title ${st.currentRole==='human'?'':'blood'}\">${roleName()}</div>${missionHtml()}${st.scarred?'<div class=\"scar\">IMMUNE · SCARRED</div>':''}${teamHtml()}${metricsHtml()}`
}
"""
    new_scene = """function lobbyScene(){
  if(!secretVisible)return `<div class=\"identity-hidden\"><div class=\"player-name\">${st.name}</div><div class=\"micro\">ROLE PREVIEW</div><div class=\"identity-mask\">IDENTITY HIDDEN</div><button class=\"role-reveal-btn\" onclick=\"revealSecret()\">Reveal role</button><div class=\"role-peek-note\">Visible for 5 seconds</div></div>`;
  return `<div class=\"player-name\">${st.name}</div><div class=\"micro\">YOUR ROLE</div><div class=\"preview-role ${st.currentRole==='human'?'':'blood'}\">${roleName()}</div><button class=\"secondary-action\" onclick=\"hideSecret()\">Hide now</button>`;
}
function idleScene(){
  if(!secretVisible)return `<div class=\"identity-hidden\"><div class=\"player-name\">${st.name}</div><div class=\"micro\">GAME IDENTITY</div><div class=\"identity-mask\">IDENTITY HIDDEN</div><button class=\"role-reveal-btn\" onclick=\"revealSecret()\">Reveal role</button><div class=\"role-peek-note\">Visible for 5 seconds</div></div>`;
  return `<div class=\"player-name\">${st.name}</div><div class=\"role-title ${st.currentRole==='human'?'':'blood'}\">${roleName()}</div>${missionHtml()}${st.scarred?'<div class=\"scar\">IMMUNE · SCARRED</div>':''}${teamHtml()}${metricsHtml()}<button class=\"secondary-action\" onclick=\"hideSecret()\">Hide now</button>`
}
"""
    if old_scene not in html:
        raise SystemExit('player hotfix: idleScene fragment not found')
    html = html.replace(old_scene, new_scene, 1)

    old_render = """function render(){
  if(!st)return;
  sunriseTime.textContent=fmtSec(st.remainingSec);
  if(st.status==='finished'&&st.endingSequence){app.innerHTML=endingScene();alertSetup.innerHTML='';return}
"""
    new_render = """function render(){
  if(!st)return;
  sunriseTime.textContent=fmtSec(st.remainingSec);
  if(st.status==='lobby'){app.innerHTML=lobbyScene();renderAlertSetup();return}
  if(st.status==='finished'&&st.endingSequence){app.innerHTML=endingScene();alertSetup.innerHTML='';return}
"""
    if old_render not in html:
        raise SystemExit('player hotfix: render fragment not found')
    html = html.replace(old_render, new_render, 1)

    # Include secret visibility in the scene key if the old scene key is still present.
    html = html.replace(
        "  return `idle:${st.initialRole}:${st.currentRole}:${st.scarred}:${st.bitesRemaining}:${st.failedBites}:${st.vampireTeam.map(x=>x.id+':'+x.original).join(',')}`;",
        "  return `idle:${st.initialRole}:${st.currentRole}:${st.scarred}:${st.bitesRemaining}:${st.failedBites}:${secretVisible}:${st.vampireTeam.map(x=>x.id+':'+x.original).join(',')}`;",
        1,
    )
    html = html.replace(
        "  if(st.status==='finished')return st.endingSequence?'ending':`finished:${st.winner?.side||''}`;",
        "  if(st.status==='lobby')return `lobby:${st.initialRole}:${secretVisible}`;\n  if(st.status==='finished')return st.endingSequence?'ending':`finished:${st.winner?.side||''}`;",
        1,
    )

player.write_text(html, encoding="utf-8")
print("Applied player hotfix: iPhone header + alerts + role privacy + pre-game preview.")
