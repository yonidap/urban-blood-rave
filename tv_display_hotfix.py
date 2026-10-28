from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
page = ROOT / "deployed" / "public" / "screen.html"
app_path = ROOT / "deployed" / "app.py"
html = page.read_text(encoding="utf-8")
app = app_path.read_text(encoding="utf-8")

MARKER = "/* v2.40 TV readability + chroma-key scar presentation */"
if MARKER in html:
    print("v2.40 TV display hotfix already applied.")
    raise SystemExit(0)

css = r'''
    /* v2.40 TV readability + chroma-key scar presentation */
    .main{width:min(1540px,96vw);height:94vh}
    .logo{font-size:clamp(22px,1.9vw,34px)}
    .rule{font-size:clamp(14px,1.1vw,20px);letter-spacing:.17em}
    .core{padding-top:2.2vh}
    .sunrise-label{font-size:clamp(18px,1.35vw,24px);letter-spacing:.32em}
    .sunrise{font-size:clamp(108px,12.2vw,210px)}
    .population{margin-top:2.2vh;width:min(1120px,90vw)}
    .pop-value{font-size:clamp(72px,7.5vw,132px)}
    .pop-label{font-size:clamp(14px,1.1vw,20px);letter-spacing:.24em;margin-top:10px}
    .bottom-zone{width:min(1460px,96vw);margin:2.8vh auto 0;gap:32px}
    .clues{gap:11px}
    .clues-heading{font-size:clamp(14px,1vw,18px);letter-spacing:.24em}
    .clue-grid{gap:10px 20px}
    .clue-row{gap:14px;padding:11px 14px;min-height:66px}
    .clue-id{font-size:clamp(12px,.85vw,15px)}
    .clue-text{font-size:clamp(18px,1.35vw,25px);line-height:1.2}
    .phone-cue{font-size:clamp(25px,2.4vw,42px);padding:20px 34px}

    .scar-gallery{grid-template-columns:repeat(2,minmax(190px,1fr));gap:12px;max-width:460px}
    .scar-person{grid-template-columns:112px 1fr;gap:13px;padding:10px 12px;min-height:92px}
    .scar-thumb{width:112px;height:74px;display:flex;align-items:center;justify-content:center;overflow:hidden}
    .scar-thumb canvas{display:block;max-width:112px;max-height:74px;width:auto;height:auto}
    .scar-person .scar-mini-copy{font-size:11px;letter-spacing:.14em;line-height:1.25}
    .scar-person .scar-mini-name{font-size:20px;margin-top:5px}

    .scar-reveal{position:absolute;inset:0;z-index:14;display:flex;align-items:center;justify-content:center;padding:2.2vh 3vw;background:radial-gradient(circle at 50% 45%,rgba(209,10,44,.14),rgba(4,2,5,.97) 62%)}
    .scar-reveal-inner{width:min(1500px,96vw);height:94vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
    .scar-reveal .event-kicker{font-size:clamp(18px,1.4vw,26px);letter-spacing:.34em}
    .scar-reveal .event-title{font-size:clamp(94px,10vw,182px);margin-top:6px;color:#c70a2b;text-shadow:0 0 34px rgba(209,10,44,.3)}
    .scar-player-name{font-size:clamp(34px,3.2vw,58px);font-weight:850;margin-top:8px;color:#fff}
    .scar-media{height:min(62vh,700px);width:min(86vw,1240px);margin-top:10px;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden}
    .scar-media canvas{display:block;max-width:100%;max-height:100%;width:auto;height:auto;filter:drop-shadow(0 18px 34px rgba(0,0,0,.44))}
    .chroma-source{position:absolute!important;width:2px!important;height:2px!important;opacity:.001!important;pointer-events:none!important;left:-9999px!important;top:-9999px!important}
    @media(max-width:1050px){.scar-gallery{grid-template-columns:repeat(2,minmax(180px,1fr));max-width:460px}.scar-person{grid-template-columns:100px 1fr;text-align:left}.scar-thumb{width:100px}.scar-thumb canvas{max-width:100px}}
'''
if "</style>" not in html:
    raise SystemExit("v2.40 TV hotfix: </style> not found")
html = html.replace("</style>", css + "\n</style>", 1)

js = r'''
// v2.40 chroma-key scar renderer
let scarChromaGeneration=0;
function stopScarChroma(){scarChromaGeneration++}
function initChromaCanvas(video,canvas,{freeze=false}={}){
  if(!video||!canvas||video.dataset.chromaReady==='1')return;
  video.dataset.chromaReady='1';
  const generation=scarChromaGeneration;
  const gl=canvas.getContext('webgl',{alpha:true,premultipliedAlpha:false,antialias:false})||canvas.getContext('experimental-webgl',{alpha:true,premultipliedAlpha:false,antialias:false});
  if(!gl){video.style.position='static';video.style.width='100%';video.style.height='100%';video.style.opacity='1';return}
  const vs=`attribute vec2 a;varying vec2 v;void main(){v=vec2((a.x+1.0)*.5,1.0-(a.y+1.0)*.5);gl_Position=vec4(a,0.,1.);}`;
  const fs=`precision mediump float;uniform sampler2D tex;varying vec2 v;void main(){vec4 c=texture2D(tex,v);float mx=max(c.r,c.b);float dom=c.g-mx;float greenGate=smoothstep(.12,.34,c.g);float key=smoothstep(.055,.20,dom)*greenGate;float a=1.0-key;float spill=smoothstep(.018,.16,dom);c.g=mix(c.g,min(c.g,mx*1.08),spill*.92);if(a<.025)discard;gl_FragColor=vec4(c.rgb,a);}`;
  const shader=(type,src)=>{const sh=gl.createShader(type);gl.shaderSource(sh,src);gl.compileShader(sh);return sh};
  const prog=gl.createProgram();gl.attachShader(prog,shader(gl.VERTEX_SHADER,vs));gl.attachShader(prog,shader(gl.FRAGMENT_SHADER,fs));gl.linkProgram(prog);gl.useProgram(prog);
  const buf=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buf);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]),gl.STATIC_DRAW);
  const loc=gl.getAttribLocation(prog,'a');gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,2,gl.FLOAT,false,0,0);
  const tex=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,tex);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
  const size=()=>{const w=video.videoWidth||1280,h=video.videoHeight||720;canvas.width=w;canvas.height=h;gl.viewport(0,0,w,h)};
  const draw=()=>{if(!video.videoWidth)return;try{gl.bindTexture(gl.TEXTURE_2D,tex);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,video);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);gl.drawArrays(gl.TRIANGLES,0,6)}catch(_){}};
  const tick=()=>{if(generation!==scarChromaGeneration||!canvas.isConnected)return;draw();requestAnimationFrame(tick)};
  const ready=()=>{size();if(freeze){try{video.currentTime=Math.max(0,(video.duration||0)-.06)}catch(_){draw()}}else tick()};
  video.addEventListener('loadedmetadata',ready,{once:true});
  if(freeze)video.addEventListener('seeked',()=>{draw();video.pause()});
  if(video.readyState>=1)ready();
}
function mountScarChroma(){
  document.querySelectorAll('[data-chroma-video]').forEach(w=>{const v=w.querySelector('video'),c=w.querySelector('canvas');initChromaCanvas(v,c,{freeze:w.dataset.freeze==='1'})});
}
function finishScarReveal(){
  stopScarChroma();
  if(!s)return;
  root.innerHTML=mainScreen();
  if(typeof lastSceneKind!=='undefined')lastSceneKind='main';
  requestAnimationFrame(mountScarChroma);
}
function scarRevealHtml(r){
  const src=r.video||'';
  return `<div class="scar-reveal"><div class="scar-reveal-inner"><div class="event-kicker">BITE REJECTED</div><div class="event-title">SCARRED</div><div class="scar-player-name">${esc(r.player)}</div>${src?`<div class="scar-media" data-chroma-video><video class="chroma-source" src="${src}" autoplay muted playsinline preload="auto" onended="finishScarReveal()" onerror="finishScarReveal()"></video><canvas></canvas></div>`:''}</div></div>`;
}
'''
anchor = "function scarGalleryHtml(){"
if anchor not in html:
    raise SystemExit("v2.40 TV hotfix: scarGalleryHtml anchor not found")
html = html.replace(anchor, js + "\n" + anchor, 1)

html, n = re.subn(
    r"function scarGalleryHtml\(\)\{.*?\n\}",
    r'''function scarGalleryHtml(){
  if(!s?.scarLoop?.length) return '';
  return `<div class="scar-gallery">${s.scarLoop.map(x=>`<div class="scar-person">${x.video?`<div class="scar-thumb" data-chroma-video data-freeze="1"><video class="chroma-source" src="${x.video}" muted playsinline preload="metadata"></video><canvas></canvas></div>`:''}<div class="scar-mini-copy">SCARRED<div class="scar-mini-name">${esc(x.name)}</div></div></div>`).join('')}</div>`;
}''',
    html,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit("v2.40 TV hotfix: scar gallery function not replaced")

html, n = re.subn(
    r"if\(r\.type==='scar'\)\{\s*root\.innerHTML=takeover\('BITE REJECTED','SCARRED',esc\(r\.player\),'','',r\.video\?`<video class=\"scar-video\" src=\"\$\{r\.video\}\" autoplay loop muted playsinline onerror=\"this\.style\.display='none'\"></video>`:''\);return;\s*\}",
    "if(r.type==='scar'){stopScarChroma();root.innerHTML=scarRevealHtml(r);requestAnimationFrame(mountScarChroma);return;}",
    html,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit("v2.40 TV hotfix: scar reveal branch not replaced")

old_main = "  root.innerHTML=mainScreen();\n}"
new_main = "  stopScarChroma();\n  root.innerHTML=mainScreen();requestAnimationFrame(mountScarChroma);\n}"
if old_main not in html:
    raise SystemExit("v2.40 TV hotfix: main-screen render anchor not found")
html = html.replace(old_main, new_main, 1)

old_server = "await set_reveal(dict(type='scar', player=target['name'], video=target.get('scarVideo')))"
new_server = "await set_reveal(dict(type='scar', player=target['name'], video=target.get('scarVideo')), min_real_seconds=12)"
if old_server in app:
    app = app.replace(old_server, new_server, 1)
elif new_server not in app:
    raise SystemExit("v2.40 TV hotfix: server scar reveal anchor not found")

page.write_text(html, encoding="utf-8")
app_path.write_text(app, encoding="utf-8")
print("Applied v2.40 TV readability, chroma-key scar videos, and video-ended dismissal.")
