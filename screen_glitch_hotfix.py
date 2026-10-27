from pathlib import Path

ROOT = Path(__file__).resolve().parent
page = ROOT / "deployed" / "public" / "screen.html"
html = page.read_text(encoding="utf-8")

CSS_MARKER = "/* v2.28 cinematic signal-glitch transitions */"
if CSS_MARKER not in html:
    css = r'''
    /* v2.28 cinematic signal-glitch transitions */
    #root.glitch-out > *,#root.glitch-in > *{will-change:transform,filter;backface-visibility:hidden}
    #root.glitch-out > *{animation:ubrGlitchOut .11s steps(2,end) both}
    #root.glitch-in > *{animation:ubrGlitchIn .23s steps(2,end) both}
    #root.glitch-out .event-title,#root.glitch-out .event-copy,#root.glitch-out .sunrise,#root.glitch-out .lobby-title,#root.glitch-out .end-title,#root.glitch-out .chosen-name,
    #root.glitch-in .event-title,#root.glitch-in .event-copy,#root.glitch-in .sunrise,#root.glitch-in .lobby-title,#root.glitch-in .end-title,#root.glitch-in .chosen-name{animation:ubrTextGlitch .23s steps(2,end) both}
    #root.glitch-out::after,#root.glitch-in::after{content:"";position:fixed;inset:0;z-index:9998;pointer-events:none;background:repeating-linear-gradient(180deg,rgba(255,255,255,.055) 0 1px,transparent 1px 5px);mix-blend-mode:screen;animation:ubrScanBurst .23s steps(2,end) both}
    @keyframes ubrGlitchOut{0%{transform:translate(0);filter:none;opacity:1}28%{transform:translate(-7px,1px) skewX(.5deg);filter:contrast(1.15)}55%{transform:translate(6px,-1px) skewX(-.4deg);filter:contrast(1.35)}78%{transform:translate(-3px,0);opacity:.82}100%{transform:translate(2px,0);opacity:.15}}
    @keyframes ubrGlitchIn{0%{transform:translate(-8px,1px) skewX(.6deg);filter:contrast(1.45);opacity:.2}18%{transform:translate(7px,-1px) skewX(-.5deg);opacity:.92}38%{transform:translate(-4px,0);filter:contrast(1.2)}58%{transform:translate(3px,1px)}76%{transform:translate(-1px,0)}100%{transform:translate(0);filter:none;opacity:1}}
    @keyframes ubrTextGlitch{0%,100%{text-shadow:inherit}16%{text-shadow:-4px 0 rgba(255,0,55,.75),4px 0 rgba(0,220,255,.55)}34%{text-shadow:3px 0 rgba(255,0,55,.55),-3px 0 rgba(0,220,255,.45)}58%{text-shadow:-2px 0 rgba(255,0,55,.45),2px 0 rgba(0,220,255,.35)}76%{text-shadow:1px 0 rgba(255,0,55,.3),-1px 0 rgba(0,220,255,.25)}}
    @keyframes ubrScanBurst{0%{opacity:0;transform:translateY(-2%)}20%{opacity:.34}45%{opacity:.12;transform:translateY(1%)}70%{opacity:.25;transform:translateY(-1%)}100%{opacity:0;transform:translateY(0)}}
    @media (prefers-reduced-motion:reduce){#root.glitch-out > *,#root.glitch-in > *,#root.glitch-out .event-title,#root.glitch-in .event-title{animation:none!important}#root.glitch-out::after,#root.glitch-in::after{display:none!important}}
'''
    if "</style>" not in html:
        raise SystemExit("v2.28 glitch hotfix: </style> not found")
    html = html.replace("</style>", css + "\n</style>", 1)

JS_MARKER = "// v2.28 signal-glitch transition controller"
if JS_MARKER not in html:
    anchor = "let socket;\n"
    if anchor not in html:
        raise SystemExit("v2.28 glitch hotfix: socket anchor not found")
    js = r'''
// v2.28 signal-glitch transition controller
let glitchSeq=0,glitchTimer=null,glitchCleanup=null;
function clearGlitchClasses(){root.classList.remove('glitch-out','glitch-in')}
function transitionRender(){
  const seq=++glitchSeq;
  if(glitchTimer)clearTimeout(glitchTimer);
  if(glitchCleanup)clearTimeout(glitchCleanup);
  clearGlitchClasses();
  const hasScene=!!root.firstElementChild;
  if(!hasScene){
    render();
    void root.offsetWidth;
    root.classList.add('glitch-in');
    glitchCleanup=setTimeout(()=>{if(seq===glitchSeq)clearGlitchClasses()},240);
    return;
  }
  root.classList.add('glitch-out');
  glitchTimer=setTimeout(()=>{
    if(seq!==glitchSeq)return;
    clearGlitchClasses();
    render();
    void root.offsetWidth;
    root.classList.add('glitch-in');
    glitchCleanup=setTimeout(()=>{if(seq===glitchSeq)clearGlitchClasses()},240);
  },105);
}
'''
    html = html.replace(anchor, anchor + js + "\n", 1)

old = "  lastRenderKey=key;\n  render();\n"
new = "  lastRenderKey=key;\n  transitionRender();\n"
if new not in html:
    if old not in html:
        raise SystemExit("v2.28 glitch hotfix: requestRender render call not found")
    html = html.replace(old, new, 1)

page.write_text(html, encoding="utf-8")
print("Applied v2.28 main-screen glitch transitions.")
