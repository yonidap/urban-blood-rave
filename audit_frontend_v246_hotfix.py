from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
player_path = ROOT / "deployed" / "public" / "player.html"
host_path = ROOT / "deployed" / "public" / "host.html"
screen_path = ROOT / "deployed" / "public" / "screen.html"

# ---------------- Player PWA ----------------
player = player_path.read_text(encoding="utf-8")
PLAYER_MARKER = "// v2.46 player safety + presence"
if PLAYER_MARKER not in player:
    css = r'''
    #ubrConnection{display:none;position:absolute;top:calc(env(safe-area-inset-top) + 6px);left:50%;transform:translateX(-50%);z-index:50;padding:6px 10px;border:1px solid rgba(209,10,44,.45);border-radius:999px;background:rgba(8,3,5,.92);color:#f4e9ee;font-family:var(--mono);font-size:9px;letter-spacing:.14em;text-transform:uppercase;pointer-events:none}
    #ubrConnection.show{display:block}
'''
    if "</style>" not in player:
        raise SystemExit("v2.46 frontend: player </style> missing")
    player = player.replace("</style>", css + "\n</style>", 1)
    if "<script>" not in player:
        raise SystemExit("v2.46 frontend: player <script> missing")
    player = player.replace("<script>", '<div id="ubrConnection">RECONNECTING…</div>\n<script>', 1)

    old_visibility = "document.addEventListener('visibilitychange',()=>{if(document.hidden)resetSecretVisibility()});\nwindow.addEventListener('pagehide',resetSecretVisibility);"
    new_visibility = "document.addEventListener('visibilitychange',()=>{if(document.hidden){resetSecretVisibility();if(st)requestRender(true)}});\nwindow.addEventListener('pagehide',()=>{resetSecretVisibility();if(st)requestRender(true)});"
    if old_visibility not in player:
        raise SystemExit("v2.46 frontend: role privacy visibility anchor missing")
    player = player.replace(old_visibility, new_visibility, 1)

    old_alert = "if(pushSubscribed){\n    alertSetup.innerHTML='<span>ACTION ALERTS ON</span> <button class=\"notify-btn\" onclick=\"testAlert()\">TEST ALERT</button>';return\n  }"
    new_alert = "if(pushSubscribed){\n    alertSetup.innerHTML=st?.status==='lobby'?'<span>ACTION ALERTS ON</span> <button class=\"notify-btn\" onclick=\"testAlert()\">TEST ALERT</button>':'<span>ACTION ALERTS ON</span>';return\n  }"
    if old_alert not in player:
        raise SystemExit("v2.46 frontend: subscribed alert branch missing")
    player = player.replace(old_alert, new_alert, 1)

    player_js = r'''
// v2.46 player safety + presence
const ubrConnection=document.getElementById('ubrConnection');
let ubrPresenceFailures=0;
async function ubrPresencePing(){
  if(document.visibilityState==='hidden')return;
  try{
    const r=await fetch(`/api/player/${token}/presence`,{method:'POST',cache:'no-store'});
    if(!r.ok)throw new Error(String(r.status));
    ubrPresenceFailures=0;
    ubrConnection?.classList.remove('show');
  }catch(_){
    ubrPresenceFailures++;
    if(ubrPresenceFailures>=2)ubrConnection?.classList.add('show');
  }
}
setInterval(ubrPresencePing,15000);
setTimeout(ubrPresencePing,300);
window.addEventListener('pageshow',ubrPresencePing);
window.addEventListener('focus',ubrPresencePing);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)ubrPresencePing()});

// A vote is final after the first successful cast. The server enforces this too;
// the client guard prevents an unnecessary second request/tap.
if(typeof castVote==='function'){
  const ubrOriginalCastVote=castVote;
  castVote=async function(targetId){
    if(st?.vote)return;
    return ubrOriginalCastVote(targetId);
  };
}
'''
    player = player.replace("</script>", player_js + "\n</script>", 1)
    player_path.write_text(player, encoding="utf-8")

# ---------------- Host console ----------------
host = host_path.read_text(encoding="utf-8")
HOST_MARKER = "// v2.46 host party-safety console"
if HOST_MARKER not in host:
    if '<div id="top" class="card">Loading...</div>' not in host:
        raise SystemExit("v2.46 frontend: host top card anchor missing")
    host = host.replace(
        '<div id="top" class="card">Loading...</div>',
        '<div id="top" class="card">Loading...</div>\n  <div id="readiness" class="card"></div>',
        1,
    )
    host = host.replace("let s;\n", "let s;\nlet readiness={players:[],scheduler:{ok:true}};\n", 1)

    safe_js = r'''
// v2.46 host party-safety console
async function refreshReadiness(){
  try{
    const r=await fetch(`/api/host/readiness?key=${encodeURIComponent(key)}`,{cache:'no-store'});
    if(r.ok){readiness=await r.json();requestRender()}
  }catch(_){}
}
setInterval(refreshReadiness,5000);
setTimeout(refreshReadiness,400);

function notReadyPlayers(){
  return (readiness.players||[]).filter(p=>!p.online||!p.pushReady);
}
async function safeStart(){
  const missing=notReadyPlayers();
  if(missing.length){
    const names=missing.map(p=>`${p.name}${!p.online?' offline':''}${!p.pushReady?' no-push':''}`).join(', ');
    if(!confirm(`Some players are not fully ready:\n${names}\n\nStart anyway?`))return;
  }
  await post('/api/host/start');
}
async function safeReset(){
  if(!confirm('RESET THE ENTIRE GAME?\n\nThis clears all roles, votes, bites and current progress.'))return;
  if(!confirm('FINAL CONFIRMATION: reset now?'))return;
  await post('/api/host/reset');
}
async function safeResolveVote(){
  const alive=(s.players||[]).filter(p=>p.alive!==false);
  const missing=alive.filter(p=>!p.vote).length;
  if(missing>0 && !confirm(`${missing} living player(s) have not voted yet. Resolve the vote anyway?`))return;
  await post('/api/host/resolve-vote');
}
async function manualPost(path,label){
  if(!confirm(`Manual override: ${label}?`))return;
  await post(path);
}
'''
    anchor = "async function configureTest(){"
    if anchor not in host:
        raise SystemExit("v2.46 frontend: configureTest anchor missing")
    host = host.replace(anchor, safe_js + "\n" + anchor, 1)

    host = host.replace("onclick=\"post('/api/host/start')\"", "onclick=\"safeStart()\"", 1)
    host = host.replace("onclick=\"post('/api/host/reset')\"", "onclick=\"safeReset()\"", 1)
    host = host.replace("onclick=\"post('/api/host/resolve-vote')\"", "onclick=\"safeResolveVote()\"", 1)

    # Render readiness before the role/spoiler-heavy player state.
    players_anchor = "  document.getElementById('players').innerHTML=`<h2>Players</h2><div class=\"list\">${s.players.map(p=>`"
    if players_anchor not in host:
        raise SystemExit("v2.46 frontend: host players render anchor missing")
    readiness_render = r'''  const rp=readiness.players||[];
  const readyCount=rp.filter(p=>p.online&&p.pushReady).length;
  const schedulerOk=readiness.scheduler?.ok!==false;
  document.getElementById('readiness').innerHTML=`
    <h2>Preflight · ${readyCount}/${rp.length||13} ready</h2>
    <div class="notice">Scheduler: <b>${schedulerOk?'READY':'CHECK SERVER'}</b>${readiness.scheduler?.lastError?` · ${readiness.scheduler.lastError}`:''}</div>
    <div class="list" style="margin-top:10px">${rp.map(p=>`<div><b>${p.name}</b> · ${p.online?'🟢 ONLINE':'🔴 OFFLINE'} · ${p.pushReady?'🔔 PUSH':'⚠️ NO PUSH'}</div>`).join('')}</div>`;

'''
    host = host.replace(players_anchor, readiness_render + players_anchor, 1)

    # Collapse spoiler-heavy state by default.
    host = host.replace(
        "document.getElementById('players').innerHTML=`<h2>Players</h2><div class=\"list\">",
        "document.getElementById('players').innerHTML=`<details><summary><b>GAME STATE · SPOILERS</b></summary><h2>Players</h2><div class=\"list\">",
        1,
    )
    host = host.replace("${p.vote?` · voted→${p.vote}`:''}</div>`).join('')}</div>`;", "${p.vote?` · voted→${p.vote}`:''}</div>`).join('')}</div></details>`;", 1)

    # Replace the manual-control block with a phase-aware, collapsed version.
    pattern = re.compile(r"  const manualDisabled=.*?\n\s*document\.getElementById\('manual'\)\.innerHTML=`.*?`;\n\n  const localHost=", re.S)
    replacement = r'''  const manualIdle=s.status==='running' && !s.biteWindow && !s.votesOpen && s.phase==='running';
  const manualDisabled=manualIdle?'':'disabled';
  document.getElementById('manual').innerHTML=`
    <details>
      <summary><b>ADVANCED MANUAL OVERRIDES</b></summary>
      <div class="notice" style="margin-top:10px">Disabled while a bite window, discussion or vote is active. Use only for recovery/testing.</div>
      <p>${s.clues.map((c,i)=>`<button class="btn" ${manualDisabled} onclick="manualPost('/api/host/clue/${i}','Clue ${i+1}')">Clue ${i+1}</button>`).join(' ')}</p>
      <p>
        <button class="btn" ${manualDisabled} onclick="manualPost('/api/host/bite-window/1','Bite Window 1')">Bite Window 1</button>
        <button class="btn" ${manualDisabled} onclick="manualPost('/api/host/bite-window/2','Bite Window 2')">Bite Window 2</button>
        <button class="btn" ${manualDisabled} onclick="manualPost('/api/host/bite-window/3','Bite Window 3')">Bite Window 3</button>
      </p>
      <p>
        <button class="btn" ${manualDisabled} onclick="manualPost('/api/host/discussion/1','Discussion 1')">Discussion 1</button>
        <button class="btn" ${manualDisabled} onclick="manualPost('/api/host/vote/1','Vote 1')">Vote 1</button>
        <button class="btn" ${manualDisabled} onclick="manualPost('/api/host/discussion/2','Discussion 2')">Discussion 2</button>
        <button class="btn" ${manualDisabled} onclick="manualPost('/api/host/vote/2','Vote 2')">Vote 2</button>
        <button class="btn" ${manualDisabled} onclick="manualPost('/api/host/discussion/3','Discussion 3')">Discussion 3</button>
        <button class="btn" ${manualDisabled} onclick="manualPost('/api/host/vote/3','Vote 3')">Vote 3</button>
      </p>
      ${s.eventLog?.length?`<h3>Recent events</h3><div class="small">${s.eventLog.slice(-8).reverse().map(e=>JSON.stringify(e)).join('<br>')}</div>`:''}
    </details>`;

  const localHost='''
    host, n = pattern.subn(replacement, host, count=1)
    if n != 1:
        raise SystemExit("v2.46 frontend: host manual block not found")
    host_path.write_text(host, encoding="utf-8")

# ---------------- Main screen connectivity ----------------
screen = screen_path.read_text(encoding="utf-8")
SCREEN_MARKER = "// v2.46 screen connectivity watchdog"
if SCREEN_MARKER not in screen:
    css = r'''
    #ubrConnWatch{display:none;position:fixed;left:50%;bottom:18px;transform:translateX(-50%);z-index:19000;padding:7px 12px;border:1px solid rgba(255,255,255,.20);border-radius:999px;background:rgba(5,4,7,.88);color:rgba(255,255,255,.82);font:700 11px/1 monospace;letter-spacing:.14em;text-transform:uppercase;pointer-events:none}
    #ubrConnWatch.show{display:block}
'''
    screen = screen.replace("</style>", css + "\n</style>", 1)
    screen = screen.replace("<script>", '<div id="ubrConnWatch">RECONNECTING…</div>\n<script>', 1)
    js = r'''
// v2.46 screen connectivity watchdog
const ubrConnWatch=document.getElementById('ubrConnWatch');
let ubrConnFailures=0;
async function ubrScreenHealth(){
  try{
    const r=await fetch('/api/screen/state?ubrHealth='+Date.now(),{cache:'no-store'});
    if(!r.ok)throw new Error(String(r.status));
    ubrConnFailures=0;ubrConnWatch?.classList.remove('show');
  }catch(_){
    ubrConnFailures++;if(ubrConnFailures>=2)ubrConnWatch?.classList.add('show');
  }
}
setInterval(ubrScreenHealth,5000);setTimeout(ubrScreenHealth,700);
'''
    screen = screen.replace("</script>", js + "\n</script>", 1)
    screen_path.write_text(screen, encoding="utf-8")

print("Applied v2.46 frontend audit hardening: preflight, confirmations, presence, privacy and connectivity.")
