from pathlib import Path

ROOT = Path(__file__).resolve().parent
page = ROOT / "deployed" / "public" / "screen.html"
html = page.read_text(encoding="utf-8")

MARKER = "/* v2.42 TV tuning + Yakir black-key + scar-return blood */"
if MARKER in html:
    print("v2.42 TV tuning hotfix already applied.")
    raise SystemExit(0)

css = r'''
    /* v2.42 TV tuning + Yakir black-key + scar-return blood */
    .sunrise{font-size:clamp(136px,12.9vw,242px)}
    .pop-value{font-size:clamp(73px,6.6vw,123px)}
'''
if "</style>" not in html:
    raise SystemExit("v2.42 TV tuning: </style> not found")
html = html.replace("</style>", css + "\n</style>", 1)

old_shader = "  const fs=`precision mediump float;uniform sampler2D tex;varying vec2 v;void main(){vec4 c=texture2D(tex,v);float mx=max(c.r,c.b);float dom=c.g-mx;float greenGate=smoothstep(.12,.34,c.g);float key=smoothstep(.055,.20,dom)*greenGate;float a=1.0-key;float spill=smoothstep(.018,.16,dom);c.g=mix(c.g,min(c.g,mx*1.08),spill*.92);if(a<.025)discard;gl_FragColor=vec4(c.rgb,a);}`;"
new_shader = "  const isYakir=/\\/yakir\\.mp4(?:[?#]|$)/i.test(video.currentSrc||video.src||'');\n  const fs=isYakir\n    ?`precision mediump float;uniform sampler2D tex;varying vec2 v;void main(){vec4 c=texture2D(tex,v);float hi=max(max(c.r,c.g),c.b);float lo=min(min(c.r,c.g),c.b);float chroma=hi-lo;float blackKey=1.0-smoothstep(.018,.085,hi);blackKey*=1.0-smoothstep(.035,.12,chroma);float a=1.0-blackKey;if(a<.025)discard;gl_FragColor=vec4(c.rgb,a);}`\n    :`precision mediump float;uniform sampler2D tex;varying vec2 v;void main(){vec4 c=texture2D(tex,v);float mx=max(c.r,c.b);float dom=c.g-mx;float greenGate=smoothstep(.12,.34,c.g);float key=smoothstep(.055,.20,dom)*greenGate;float a=1.0-key;float spill=smoothstep(.018,.16,dom);c.g=mix(c.g,min(c.g,mx*1.08),spill*.92);if(a<.025)discard;gl_FragColor=vec4(c.rgb,a);}`;"
if old_shader not in html:
    raise SystemExit("v2.42 TV tuning: chroma shader anchor not found")
html = html.replace(old_shader, new_shader, 1)

old_finish = '''function finishScarReveal(){
  scarDismissedKey=scarRevealKey(s?.reveal);
  stopScarChroma();
  if(!s)return;
  root.innerHTML=mainScreen();
  if(typeof lastSceneKind!=='undefined')lastSceneKind='main';
  requestAnimationFrame(mountScarChroma);
}'''
new_finish = '''function scarReturnWithBlood(){
  const seq=++transitionSeq;
  if(transitionTimer)clearTimeout(transitionTimer);
  if(transitionCleanup)clearTimeout(transitionCleanup);
  clearTransitionClasses();
  void bloodOverlay.offsetWidth;
  bloodOverlay.classList.add('cover');
  transitionTimer=setTimeout(()=>{
    if(seq!==transitionSeq)return;
    root.innerHTML=mainScreen();
    if(typeof lastSceneKind!=='undefined')lastSceneKind='main';
    requestAnimationFrame(mountScarChroma);
    bloodOverlay.classList.remove('cover');
    void bloodOverlay.offsetWidth;
    bloodOverlay.classList.add('reveal');
    transitionCleanup=setTimeout(()=>{if(seq===transitionSeq)bloodOverlay.classList.remove('reveal')},735);
  },790);
}
function finishScarReveal(){
  scarDismissedKey=scarRevealKey(s?.reveal);
  stopScarChroma();
  if(!s)return;
  scarReturnWithBlood();
}'''
if old_finish not in html:
    raise SystemExit("v2.42 TV tuning: finishScarReveal anchor not found")
html = html.replace(old_finish, new_finish, 1)

page.write_text(html, encoding="utf-8")
print("Applied v2.42 TV size tuning, Yakir black-key transparency, and blood return after scar video.")
