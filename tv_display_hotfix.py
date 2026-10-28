from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
page = ROOT / "deployed" / "public" / "screen.html"
app_path = ROOT / "deployed" / "app.py"
html = page.read_text(encoding="utf-8")
app = app_path.read_text(encoding="utf-8")

MARKER = "/* v2.41 TV XL + reliable chroma-key scar playback */"
if MARKER in html:
    print("v2.41 TV display hotfix already applied.")
    raise SystemExit(0)

css = r'''
    /* v2.41 TV XL + reliable chroma-key scar playback */
    .main{width:min(1760px,98vw);height:96vh}
    .logo{font-size:clamp(36px,2.7vw,54px)}
    .rule{font-size:clamp(21px,1.55vw,30px);letter-spacing:.14em;font-weight:750}
    .core{padding-top:1.2vh}
    .sunrise-label{font-size:clamp(27px,1.8vw,36px);letter-spacing:.28em;font-weight:800}
    .sunrise{font-size:clamp(160px,15.2vw,285px);line-height:.82}
    .population{margin-top:1.8vh;width:min(1320px,94vw)}
    .pop-value{font-size:clamp(104px,9.4vw,176px);line-height:.9}
    .pop-label{font-size:clamp(20px,1.5vw,29px);letter-spacing:.20em;margin-top:12px;font-weight:800}
    .bottom-zone{width:min(1680px,97vw);margin:2.0vh auto 0;gap:26px;align-items:start}
    .clues{gap:12px}
    .clues-heading{font-size:clamp(20px,1.45vw,27px);letter-spacing:.20em;font-weight:800}
    .clue-grid{gap:11px 22px}
    .clue-row{gap:16px;padding:14px 17px;min-height:78px}
    .clue-id{font-size:clamp(15px,1.05vw,20px);font-weight:850}
    .clue-text{font-size:clamp(24px,1.8vw,34px);line-height:1.16;font-weight:650}
    .phone-cue{font-size:clamp(34px,3vw,56px);padding:24px 42px}

    .scar-gallery{grid-template-columns:repeat(2,minmax(300px,1fr));gap:16px;max-width:760px;width:100%}
    .scar-person{grid-template-columns:190px 1fr;gap:18px;padding:14px 16px;min-height:148px;align-items:center}
    .scar-thumb{width:190px;height:122px;display:flex;align-items:center;justify-content:center;overflow:hidden;position:relative}
    .scar-thumb canvas{display:block;max-width:190px;max-height:122px;width:auto;height:auto}
    .scar-person .scar-mini-copy{font-size:16px;letter-spacing:.12em;line-height:1.2;font-weight:800}
    .scar-person .scar-mini-name{font-size:clamp(28px,2vw,36px);margin-top:8px;font-weight:900}

    .scar-reveal{position:absolute;inset:0;z-index:14;display:flex;align-items:center;justify-content:center;padding:1vh 2vw;background:radial-gradient(circle at 50% 44%,rgba(209,10,44,.17),rgba(4,2,5,.98) 64%)}
    .scar-reveal-inner{width:min(1740px,98vw);height:97vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
    .scar-reveal .event-kicker{font-size:clamp(27px,1.9vw,38px);letter-spacing:.28em;font-weight:850}
    .scar-reveal .event-title{font-size:clamp(126px,12vw,224px);line-height:.82;margin-top:4px;color:#c70a2b;text-shadow:0 0 42px rgba(209,10,44,.34)}
    .scar-player-name{font-size:clamp(48px,4vw,76px);font-weight:900;margin-top:8px;color:#fff}
    .scar-media{height:min(70vh,790px);width:min(92vw,1480px);margin-top:6px;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden}
    .scar-media canvas{display:block;max-width:100%;max-height:100%;width:auto;height:auto;position:relative;z-index:2;filter:drop-shadow(0 20px 38px rgba(0,0,0,.46))}
    .chroma-source{position:absolute!important;inset:0!important;width:100%!important;height:100%!important;object-fit:contain!important;opacity:.001!important;pointer-events:none!important;z-index:1!important}
    @media(max-width:1200px){
      .scar-gallery{grid-template-columns:repeat(2,minmax(255px,1fr));max-width:680px}
      .scar-person{grid-template-columns:165px 1fr;min-height:132px}.scar-thumb{width:165px;height:108px}.scar-thumb canvas{max-width:165px;max-height:108px}
    }
'''
if "</style>" not in html:
    raise SystemExit("v2.41 TV hotfix: </style> not found")
html = html.replace("</style>", css + "\n</style>", 1)

js = r'''
// v2.41 reliable chroma-key scar renderer
let scarChromaGeneration=0;
let scarDismissedKey=null;
function scarRevealKey(r){return r?`${r.player||''}|${r.video||''}`:''}
function stopScarChroma(){scarChromaGeneration++}
function initChromaCanvas(video,canvas,{freeze=false}={}){
  if(!video||!canvas||video.dataset.chromaReady==='1')return;
  video.dataset.chromaReady='1';
  const generation=scarChromaGeneration;
  const gl=canvas.getContext('webgl',{alpha:true,premultipliedAlpha:false,antialias:false})||canvas.getContext('experimental-webgl',{alpha:true,premultipliedAlpha:false,antialias:false});
  if(!gl){video.style.opacity='1';return}
  const vs=`attribute vec2 a;varying vec2 v;void main(){v=vec2((a.x+1.0)*.5,1.0-(a.y+1.0)*.5);gl_Position=vec4(a,0.,1.);}`;
  const fs=`precision mediump float;uniform sampler2D tex;varying vec2 v;void main(){vec4 c=texture2D(tex,v);float mx=max(c.r,c.b);float dom=c.g-mx;float greenGate=smoothstep(.12,.34,c.g);float key=smoothstep(.055,.20,dom)*greenGate;float a=1.0-key;float spill=smoothstep(.018,.16,dom);c.g=mix(c.g,min(c.g,mx*1.08),spill*.92);if(a<.025)discard;gl_FragColor=vec4(c.rgb,a);}`;
  const shader=(type,src)=>{const sh=gl.createShader(type);gl.shaderSource(sh,src);gl.compileShader(sh);return sh};
  const prog=gl.createProgram();gl.attachShader(prog,shader(gl.VERTEX_SHADER,vs));gl.attachShader(prog,shader(gl.FRAGMENT_SHADER,fs));gl.linkProgram(prog);gl.useProgram(prog);
  const buf=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buf);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]),gl.STATIC_DRAW);
  const loc=gl.getAttribLocation(prog,'a');gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,2,gl.FLOAT,false,0,0);
  const tex=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,tex);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
  const size=()=>{const w=video.videoWidth||1280,h=video.videoHeight||720;canvas.width=w;canvas.height=h;gl.viewport(0,0,w,h)};
  const draw=()=>{if(!video.videoWidth)return;try{gl.bindTexture(gl.TEXTURE_2D,tex);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,video);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);gl.drawArrays(gl.TRIANGLES,0,6)}catch(_){}};
  let started=false;
  const rafLoop=()=>{if(generation!==scarChromaGeneration||!canvas.isConnected)return;draw();requestAnimationFrame(rafLoop)};
  const frameLoop=()=>{if(generation!==scarChromaGeneration||!canvas.isConnected)return;draw();video.requestVideoFrameCallback(frameLoop)};
  const startPlayback=()=>{
    if(started||generation!==scarChromaGeneration||!canvas.isConnected)return;started=true;size();
    if(freeze){
      const seek=()=>{try{video.currentTime=Math.max(0,(Number.isFinite(video.duration)?video.duration:0)-.08)}catch(_){draw()}};
      video.addEventListener('seeked',()=>{draw();video.pause()},{once:true});seek();return;
    }
    const p=video.play();if(p&&typeof p.catch==='function')p.catch(()=>{});
    if(typeof video.requestVideoFrameCallback==='function')video.requestVideoFrameCallback(frameLoop);else requestAnimationFrame(rafLoop);
  };
  video.addEventListener('loadeddata',startPlayback,{once:true});
  video.addEventListener('canplay',startPlayback,{once:true});
  if(video.readyState>=2)startPlayback();
}
function mountScarChroma(){
  document.querySelectorAll('[data-chroma-video]').forEach(w=>{const v=w.querySelector('video'),c=w.querySelector('canvas');initChromaCanvas(v,c,{freeze:w.dataset.freeze==='1'})});
}
function finishScarReveal(){
  scarDismissedKey=scarRevealKey(s?.reveal);
  stopScarChroma();
  if(!s)return;
  root.innerHTML=mainScreen();
  if(typeof lastSceneKind!=='undefined')lastSceneKind='main';
  requestAnimationFrame(mountScarChroma);
}
function scarRevealHtml(r){
  const src=r.video||'';
  return `<div class="scar-reveal"><div class="scar-reveal-inner"><div class="event-kicker">BITE REJECTED</div><div class="event-title">SCARRED</div><div class="scar-player-name">${esc(r.player)}</div>${src?`<div class="scar-media" data-chroma-video><video class="chroma-source" src="${src}" muted playsinline preload="auto" onended="finishScarReveal()" onerror="finishScarReveal()"></video><canvas></canvas></div>`:''}</div></div>`;
}
'''
anchor = "function scarGalleryHtml(){"
if anchor not in html:
    raise SystemExit("v2.41 TV hotfix: scarGalleryHtml anchor not found")
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
    raise SystemExit("v2.41 TV hotfix: scar gallery function not replaced")

html, n = re.subn(
    r"if\(r\.type==='scar'\)\{\s*root\.innerHTML=takeover\('BITE REJECTED','SCARRED',esc\(r\.player\),'','',r\.video\?`<video class=\"scar-video\" src=\"\$\{r\.video\}\" autoplay loop muted playsinline onerror=\"this\.style\.display='none'\"></video>`:''\);return;\s*\}",
    "if(r.type==='scar'){const k=scarRevealKey(r);if(scarDismissedKey===k){root.innerHTML=mainScreen();requestAnimationFrame(mountScarChroma);return;}stopScarChroma();root.innerHTML=scarRevealHtml(r);requestAnimationFrame(mountScarChroma);return;}",
    html,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit("v2.41 TV hotfix: scar reveal branch not replaced")

old_main = "  root.innerHTML=mainScreen();\n}"
new_main = "  if(!s?.reveal||s.reveal.type!=='scar')scarDismissedKey=null;\n  stopScarChroma();\n  root.innerHTML=mainScreen();requestAnimationFrame(mountScarChroma);\n}"
if old_main not in html:
    raise SystemExit("v2.41 TV hotfix: main-screen render anchor not found")
html = html.replace(old_main, new_main, 1)

old_server = "await set_reveal(dict(type='scar', player=target['name'], video=target.get('scarVideo')))"
new_server = "await set_reveal(dict(type='scar', player=target['name'], video=target.get('scarVideo')), min_real_seconds=12)"
if old_server in app:
    app = app.replace(old_server, new_server, 1)
elif new_server not in app:
    raise SystemExit("v2.41 TV hotfix: server scar reveal anchor not found")

page.write_text(html, encoding="utf-8")
app_path.write_text(app, encoding="utf-8")
print("Applied v2.41 XL TV layout and reliable chroma-key scar video playback.")
