from pathlib import Path

player = Path(__file__).resolve().parent / "deployed" / "public" / "player.html"
html = player.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str):
    global html
    if old not in html:
        raise SystemExit(f"Privacy hotfix failed: expected {label} fragment not found")
    html = html.replace(old, new, 1)

replace_once(
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
    'privacy CSS',
)

replace_once(
    "let st,previousState=null,viewMode='main',audioCtx=null,renderPending=false,lastSceneKey=null;\n",
    "let st,previousState=null,viewMode='main',audioCtx=null,renderPending=false,lastSceneKey=null;\nlet secretVisible=false,secretTimer=null;\n",
    'state vars',
)

replace_once(
    """function sceneKey(){
  if(!st)return'none';
  if(st.status==='finished')return st.endingSequence?'ending':`finished:${st.winner?.side||''}`;
  if(!st.alive)return'dead';
  if(st.votesOpen)return`vote:${st.currentRound}:${st.voteCandidates.map(x=>x.id).join(',')}`;
  if(viewMode==='bite'&&st.biteAvailable)return`bite-picker:${st.biteWindowNumber}:${st.biteCandidates.map(x=>x.id).join(',')}`;
  if(st.biteAvailable)return`bite-ready:${st.biteWindowNumber}:${st.bitesRemaining}:${st.failedBites}`;
  return `idle:${st.initialRole}:${st.currentRole}:${st.scarred}:${st.bitesRemaining}:${st.failedBites}:${st.vampireTeam.map(x=>x.id+':'+x.original).join(',')}`;
}
""",
    """function sceneKey(){
  if(!st)return'none';
  if(st.status==='lobby')return `lobby:${st.initialRole}:${secretVisible}`;
  if(st.status==='finished')return st.endingSequence?'ending':`finished:${st.winner?.side||''}`;
  if(!st.alive)return'dead';
  if(st.votesOpen)return`vote:${st.currentRound}:${st.voteCandidates.map(x=>x.id).join(',')}`;
  if(viewMode==='bite'&&st.biteAvailable)return`bite-picker:${st.biteWindowNumber}:${st.biteCandidates.map(x=>x.id).join(',')}`;
  if(st.biteAvailable)return`bite-ready:${st.biteWindowNumber}:${st.bitesRemaining}:${st.failedBites}`;
  return `idle:${st.initialRole}:${st.currentRole}:${st.scarred}:${st.bitesRemaining}:${st.failedBites}:${secretVisible}:${st.vampireTeam.map(x=>x.id+':'+x.original).join(',')}`;
}
""",
    'sceneKey',
)

replace_once(
    """function applyState(next){
  const prev=previousState;
  st=next;
  if(viewMode==='bite'&&!next.biteAvailable)viewMode='main';
""",
    """function applyState(next){
  const prev=previousState;
  if(prev&&prev.status!==next.status)resetSecretVisibility();
  st=next;
  if(viewMode==='bite'&&!next.biteAvailable)viewMode='main';
""",
    'applyState',
)

replace_once(
    "function roleName(){if(st.initialRole==='original_vampire')return'ORIGINAL VAMPIRE';if(st.currentRole==='converted')return'CONVERTED';return'HUMAN'}\n",
    "function resetSecretVisibility(){secretVisible=false;if(secretTimer){clearTimeout(secretTimer);secretTimer=null}}\n"
    "function hideSecret(){resetSecretVisibility();requestRender(true)}\n"
    "function revealSecret(){resetSecretVisibility();secretVisible=true;requestRender(true);secretTimer=setTimeout(()=>{secretVisible=false;secretTimer=null;requestRender(true)},5000)}\n"
    "document.addEventListener('visibilitychange',()=>{if(document.hidden)resetSecretVisibility()});\n"
    "window.addEventListener('pagehide',resetSecretVisibility);\n"
    "function roleName(){if(st.initialRole==='original_vampire')return'ORIGINAL VAMPIRE';if(st.currentRole==='converted')return'CONVERTED';return'HUMAN'}\n",
    'secret functions',
)

replace_once(
    """function idleScene(){
  return `<div class=\"player-name\">${st.name}</div><div class=\"role-title ${st.currentRole==='human'?'':'blood'}\">${roleName()}</div>${missionHtml()}${st.scarred?'<div class=\"scar\">IMMUNE · SCARRED</div>':''}${teamHtml()}${metricsHtml()}`
}
""",
    """function lobbyScene(){
  if(!secretVisible)return `<div class=\"identity-hidden\"><div class=\"player-name\">${st.name}</div><div class=\"micro\">ROLE PREVIEW</div><div class=\"identity-mask\">IDENTITY HIDDEN</div><button class=\"role-reveal-btn\" onclick=\"revealSecret()\">Reveal role</button><div class=\"role-peek-note\">Visible for 5 seconds</div></div>`;
  return `<div class=\"player-name\">${st.name}</div><div class=\"micro\">YOUR ROLE</div><div class=\"preview-role ${st.currentRole==='human'?'':'blood'}\">${roleName()}</div><button class=\"secondary-action\" onclick=\"hideSecret()\">Hide now</button>`;
}
function idleScene(){
  if(!secretVisible)return `<div class=\"identity-hidden\"><div class=\"player-name\">${st.name}</div><div class=\"micro\">GAME IDENTITY</div><div class=\"identity-mask\">IDENTITY HIDDEN</div><button class=\"role-reveal-btn\" onclick=\"revealSecret()\">Reveal role</button><div class=\"role-peek-note\">Visible for 5 seconds</div></div>`;
  return `<div class=\"player-name\">${st.name}</div><div class=\"role-title ${st.currentRole==='human'?'':'blood'}\">${roleName()}</div>${missionHtml()}${st.scarred?'<div class=\"scar\">IMMUNE · SCARRED</div>':''}${teamHtml()}${metricsHtml()}<button class=\"secondary-action\" onclick=\"hideSecret()\">Hide now</button>`
}
""",
    'lobby/idle scenes',
)

replace_once(
    """function render(){
  if(!st)return;
  sunriseTime.textContent=fmtSec(st.remainingSec);
  if(st.status==='finished'&&st.endingSequence){app.innerHTML=endingScene();alertSetup.innerHTML='';return}
""",
    """function render(){
  if(!st)return;
  sunriseTime.textContent=fmtSec(st.remainingSec);
  if(st.status==='lobby'){app.innerHTML=lobbyScene();renderAlertSetup();return}
  if(st.status==='finished'&&st.endingSequence){app.innerHTML=endingScene();alertSetup.innerHTML='';return}
""",
    'render lobby branch',
)

player.write_text(html, encoding="utf-8")
print("Applied v2.26.2 role privacy + pre-game role preview hotfix.")
