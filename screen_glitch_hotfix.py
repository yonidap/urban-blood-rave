from pathlib import Path

ROOT = Path(__file__).resolve().parent
page = ROOT / "deployed" / "public" / "screen.html"
html = page.read_text(encoding="utf-8")

CSS_MARKER = "/* v2.29 strong cinematic signal-glitch transitions */"
if CSS_MARKER not in html:
    css = r'''
    /* v2.29 strong cinematic signal-glitch transitions */
    #root.glitch-out > *,#root.glitch-in > *{will-change:transform,filter,opacity;backface-visibility:hidden;transform-origin:center center}
    #root.glitch-out > *{animation:ubrGlitchOut .18s steps(3,end) both}
    #root.glitch-in > *{animation:ubrGlitchIn .47s steps(6,end) both}

    #root.glitch-out .event-title,#root.glitch-out .event-copy,#root.glitch-out .sunrise,#root.glitch-out .lobby-title,#root.glitch-out .end-title,#root.glitch-out .chosen-name,#root.glitch-out .clue-text,#root.glitch-out .vote-title,
    #root.glitch-in .event-title,#root.glitch-in .event-copy,#root.glitch-in .sunrise,#root.glitch-in .lobby-title,#root.glitch-in .end-title,#root.glitch-in .chosen-name,#root.glitch-in .clue-text,#root.glitch-in .vote-title{animation:ubrTextGlitch .52s steps(6,end) both}

    #root.glitch-out::before,#root.glitch-in::before{content:"";position:fixed;inset:0;z-index:9997;pointer-events:none;background:rgba(255,255,255,.13);mix-blend-mode:screen;animation:ubrFlashBurst .52s steps(4,end) both}
    #root.glitch-out::after,#root.glitch-in::after{content:"";position:fixed;inset:0;z-index:9998;pointer-events:none;background:repeating-linear-gradient(180deg,rgba(255,255,255,.085) 0 1px,transparent 1px 5px),linear-gradient(90deg,rgba(255,0,50,.08),transparent 38%,rgba(0,220,255,.07));mix-blend-mode:screen;animation:ubrScanBurst .52s steps(5,end) both}

    @keyframes ubrGlitchOut{
      0%{transform:translate(0,0);filter:none;opacity:1}
      25%{transform:translate(-12px,2px) skewX(1deg);filter:contrast(1.28) saturate(1.18);opacity:.94}
      52%{transform:translate(10px,-2px) skewX(-.8deg);filter:contrast(1.5) saturate(1.28);opacity:.78}
      76%{transform:translate(-6px,1px);filter:contrast(1.35);opacity:.58}
      100%{transform:translate(4px,0);filter:contrast(1.6);opacity:.08}
    }
    @keyframes ubrGlitchIn{
      0%{transform:translate(-14px,2px) skewX(1.2deg);filter:contrast(1.65) saturate(1.4);opacity:.12}
      12%{transform:translate(12px,-2px) skewX(-1deg);opacity:.86}
      25%{transform:translate(-9px,1px) skewX(.65deg);filter:contrast(1.45) saturate(1.25);opacity:.68}
      39%{transform:translate(7px,-1px) skewX(-.45deg);opacity:1}
      55%{transform:translate(-5px,1px);filter:contrast(1.3);opacity:.82}
      70%{transform:translate(3px,0);filter:contrast(1.17);opacity:1}
      84%{transform:translate(-1px,0);opacity:.94}
      100%{transform:translate(0,0);filter:none;opacity:1}
    }
    @keyframes ubrTextGlitch{
      0%,100%{transform:translateX(0);text-shadow:inherit}
      10%{transform:translateX(-8px);text-shadow:-7px 0 rgba(255,0,55,.95),7px 0 rgba(0,220,255,.8)}
      22%{transform:translateX(6px);text-shadow:6px 0 rgba(255,0,55,.78),-6px 0 rgba(0,220,255,.68)}
      36%{transform:translateX(-5px);text-shadow:-5px 0 rgba(255,0,55,.72),5px 0 rgba(0,220,255,.58)}
      52%{transform:translateX(4px);text-shadow:4px 0 rgba(255,0,55,.62),-4px 0 rgba(0,220,255,.5)}
      68%{transform:translateX(-3px);text-shadow:-3px 0 rgba(255,0,55,.5),3px 0 rgba(0,220,255,.38)}
      84%{transform:translateX(1px);text-shadow:2px 0 rgba(255,0,55,.32),-2px 0 rgba(0,220,255,.28)}
    }
    @keyframes ubrFlashBurst{
      0%{opacity:0}
      8%{opacity:.55}
      16%{opacity:0}
      31%{opacity:.22}
      39%{opacity:0}
      100%{opacity:0}
    }
    @keyframes ubrScanBurst{
      0%{opacity:0;transform:translateY(-3%)}
      10%{opacity:.52;transform:translateY(1%)}
      24%{opacity:.18;transform:translateY(-2%)}
      39%{opacity:.44;transform:translateY(2%)}
      56%{opacity:.16;transform:translateY(-1%)}
      74%{opacity:.3;transform:translateY(1%)}
      100%{opacity:0;transform:translateY(0)}
    }
    @media (prefers-reduced-motion:reduce){#root.glitch-out > *,#root.glitch-in > *,#root.glitch-out .event-title,#root.glitch-in .event-title{animation:none!important}#root.glitch-out::before,#root.glitch-in::before,#root.glitch-out::after,#root.glitch-in::after{display:none!important}}
'''
    # Replace the previous v2.28 block when the source is rebuilt from an already-patched file.
    old_start = html.find("    /* v2.28 cinematic signal-glitch transitions */")
    if old_start >= 0:
        old_end = html.find("    @media (prefers-reduced-motion:reduce)", old_start)
        if old_end >= 0:
            old_end = html.find("\n", html.find("}", old_end) + 1)
        if old_end and old_end > old_start:
            html = html[:old_start] + css + html[old_end:]
        else:
            raise SystemExit("v2.29 glitch hotfix: could not replace v2.28 CSS block")
    else:
        if "</style>" not in html:
            raise SystemExit("v2.29 glitch hotfix: </style> not found")
        html = html.replace("</style>", css + "\n</style>", 1)

JS_MARKER = "// v2.29 strong signal-glitch transition controller"
if JS_MARKER not in html:
    old_marker = "// v2.28 signal-glitch transition controller"
    if old_marker in html:
        start = html.index(old_marker)
        end = html.index("\n\n", start)
        old_js = html[start:end]
        # The old controller is replaced below using a broader function block search.
        controller_start = html.index("// v2.28 signal-glitch transition controller")
        controller_end = html.index("\n\n", html.index("function transitionRender(){", controller_start))
        # Include the complete transitionRender function through its closing brace.
        controller_end = html.index("\n}\n", html.index("function transitionRender(){", controller_start)) + 3
        html = html[:controller_start] + html[controller_end:]

    anchor = "let socket;\n"
    if anchor not in html:
        raise SystemExit("v2.29 glitch hotfix: socket anchor not found")
    js = r'''
// v2.29 strong signal-glitch transition controller
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
    glitchCleanup=setTimeout(()=>{if(seq===glitchSeq)clearGlitchClasses()},500);
    return;
  }
  root.classList.add('glitch-out');
  glitchTimer=setTimeout(()=>{
    if(seq!==glitchSeq)return;
    clearGlitchClasses();
    render();
    void root.offsetWidth;
    root.classList.add('glitch-in');
    glitchCleanup=setTimeout(()=>{if(seq===glitchSeq)clearGlitchClasses()},500);
  },175);
}
'''
    html = html.replace(anchor, anchor + js + "\n", 1)

old = "  lastRenderKey=key;\n  render();\n"
new = "  lastRenderKey=key;\n  transitionRender();\n"
if new not in html:
    if old not in html:
        raise SystemExit("v2.29 glitch hotfix: requestRender render call not found")
    html = html.replace(old, new, 1)

page.write_text(html, encoding="utf-8")
print("Applied v2.29 strong main-screen glitch transitions.")
