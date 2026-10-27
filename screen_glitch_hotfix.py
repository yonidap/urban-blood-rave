from pathlib import Path

ROOT = Path(__file__).resolve().parent
page = ROOT / "deployed" / "public" / "screen.html"
html = page.read_text(encoding="utf-8")

CSS_MARKER = "/* v2.30 unmistakable viewport signal-glitch transitions */"
if CSS_MARKER not in html:
    css = r'''
    /* v2.30 unmistakable viewport signal-glitch transitions */
    #root{transform-origin:center center}
    #root.glitch-out{animation:ubrViewportOut .24s steps(4,end) both;will-change:transform,filter,opacity}
    #root.glitch-in{animation:ubrViewportIn .56s steps(8,end) both;will-change:transform,filter,opacity}

    #root.glitch-out .event-title,#root.glitch-out .event-copy,#root.glitch-out .sunrise,#root.glitch-out .lobby-title,#root.glitch-out .end-title,#root.glitch-out .chosen-name,#root.glitch-out .clue-text,#root.glitch-out .vote-title,
    #root.glitch-in .event-title,#root.glitch-in .event-copy,#root.glitch-in .sunrise,#root.glitch-in .lobby-title,#root.glitch-in .end-title,#root.glitch-in .chosen-name,#root.glitch-in .clue-text,#root.glitch-in .vote-title{animation:ubrTextGlitch .72s steps(8,end) both}

    body.ubr-glitching::before{content:"";position:fixed;inset:0;z-index:99998;pointer-events:none;background:linear-gradient(180deg,transparent 0 18%,rgba(255,255,255,.16) 18% 20%,transparent 20% 41%,rgba(210,10,44,.14) 41% 43%,transparent 43% 70%,rgba(0,220,255,.10) 70% 72%,transparent 72% 100%);mix-blend-mode:screen;animation:ubrSliceBurst .8s steps(7,end) both}
    body.ubr-glitching::after{content:"";position:fixed;inset:0;z-index:99999;pointer-events:none;background:repeating-linear-gradient(180deg,rgba(255,255,255,.10) 0 1px,transparent 1px 4px);mix-blend-mode:screen;animation:ubrScreenFlash .8s steps(7,end) both}

    @keyframes ubrViewportOut{
      0%{transform:translate3d(0,0,0);filter:none;opacity:1}
      22%{transform:translate3d(-18px,2px,0) skewX(1.4deg);filter:contrast(1.45) saturate(1.35) drop-shadow(7px 0 rgba(255,0,55,.65)) drop-shadow(-7px 0 rgba(0,220,255,.55));opacity:.96}
      48%{transform:translate3d(15px,-2px,0) skewX(-1.1deg);filter:contrast(1.75) saturate(1.5) drop-shadow(-9px 0 rgba(255,0,55,.72)) drop-shadow(9px 0 rgba(0,220,255,.62));opacity:.76}
      72%{transform:translate3d(-10px,1px,0);filter:contrast(1.55) brightness(1.15);opacity:.48}
      100%{transform:translate3d(8px,0,0);filter:contrast(1.9) brightness(.7);opacity:.04}
    }
    @keyframes ubrViewportIn{
      0%{transform:translate3d(-20px,2px,0) skewX(1.5deg);filter:contrast(1.9) saturate(1.6) drop-shadow(10px 0 rgba(255,0,55,.78)) drop-shadow(-10px 0 rgba(0,220,255,.68));opacity:.06}
      10%{transform:translate3d(17px,-2px,0) skewX(-1.2deg);opacity:.9}
      22%{transform:translate3d(-14px,1px,0);filter:contrast(1.65) saturate(1.45);opacity:.58}
      34%{transform:translate3d(12px,-1px,0);filter:contrast(1.5) drop-shadow(-7px 0 rgba(255,0,55,.6)) drop-shadow(7px 0 rgba(0,220,255,.5));opacity:1}
      47%{transform:translate3d(-9px,1px,0);filter:contrast(1.38);opacity:.76}
      60%{transform:translate3d(6px,0,0);filter:contrast(1.25);opacity:1}
      73%{transform:translate3d(-4px,0,0);filter:contrast(1.16);opacity:.9}
      86%{transform:translate3d(2px,0,0);filter:contrast(1.08);opacity:1}
      100%{transform:translate3d(0,0,0);filter:none;opacity:1}
    }
    @keyframes ubrTextGlitch{
      0%,100%{transform:translateX(0);text-shadow:inherit}
      9%{transform:translateX(-12px);text-shadow:-9px 0 rgba(255,0,55,.98),9px 0 rgba(0,220,255,.9)}
      20%{transform:translateX(9px);text-shadow:8px 0 rgba(255,0,55,.9),-8px 0 rgba(0,220,255,.8)}
      33%{transform:translateX(-8px);text-shadow:-7px 0 rgba(255,0,55,.78),7px 0 rgba(0,220,255,.68)}
      46%{transform:translateX(7px);text-shadow:6px 0 rgba(255,0,55,.7),-6px 0 rgba(0,220,255,.58)}
      59%{transform:translateX(-5px);text-shadow:-5px 0 rgba(255,0,55,.58),5px 0 rgba(0,220,255,.48)}
      72%{transform:translateX(3px);text-shadow:4px 0 rgba(255,0,55,.45),-4px 0 rgba(0,220,255,.38)}
      86%{transform:translateX(-1px);text-shadow:-2px 0 rgba(255,0,55,.28),2px 0 rgba(0,220,255,.24)}
    }
    @keyframes ubrSliceBurst{
      0%{opacity:0;transform:translateX(0)}
      8%{opacity:.95;transform:translateX(-12px)}
      18%{opacity:.18;transform:translateX(8px)}
      31%{opacity:.78;transform:translateX(15px)}
      43%{opacity:.12;transform:translateX(-8px)}
      58%{opacity:.62;transform:translateX(-14px)}
      71%{opacity:.16;transform:translateX(6px)}
      84%{opacity:.36;transform:translateX(-3px)}
      100%{opacity:0;transform:translateX(0)}
    }
    @keyframes ubrScreenFlash{
      0%{opacity:0;background-color:transparent}
      7%{opacity:.72;background-color:rgba(255,255,255,.14)}
      14%{opacity:.08;background-color:transparent}
      28%{opacity:.5;background-color:rgba(209,10,44,.09)}
      36%{opacity:.08;background-color:transparent}
      52%{opacity:.42;background-color:rgba(255,255,255,.08)}
      64%{opacity:.1;background-color:transparent}
      80%{opacity:.25}
      100%{opacity:0;background-color:transparent}
    }
'''
    if "</style>" not in html:
        raise SystemExit("v2.30 glitch hotfix: </style> not found")
    html = html.replace("</style>", css + "\n</style>", 1)

JS_MARKER = "// v2.30 unmistakable viewport glitch controller"
if JS_MARKER not in html:
    anchor = "let socket;\n"
    if anchor not in html:
        raise SystemExit("v2.30 glitch hotfix: socket anchor not found")
    js = r'''
// v2.30 unmistakable viewport glitch controller
let glitchSeq=0,glitchTimer=null,glitchCleanup=null;
function clearGlitchClasses(){root.classList.remove('glitch-out','glitch-in');document.body.classList.remove('ubr-glitching')}
function transitionRender(){
  const seq=++glitchSeq;
  if(glitchTimer)clearTimeout(glitchTimer);
  if(glitchCleanup)clearTimeout(glitchCleanup);
  clearGlitchClasses();
  document.body.classList.add('ubr-glitching');
  const hasScene=!!root.firstElementChild;
  if(!hasScene){
    render();
    void root.offsetWidth;
    root.classList.add('glitch-in');
    glitchCleanup=setTimeout(()=>{if(seq===glitchSeq)clearGlitchClasses()},820);
    return;
  }
  root.classList.add('glitch-out');
  glitchTimer=setTimeout(()=>{
    if(seq!==glitchSeq)return;
    root.classList.remove('glitch-out');
    render();
    void root.offsetWidth;
    root.classList.add('glitch-in');
    glitchCleanup=setTimeout(()=>{if(seq===glitchSeq)clearGlitchClasses()},590);
  },235);
}
'''
    html = html.replace(anchor, anchor + js + "\n", 1)

old = "  lastRenderKey=key;\n  render();\n"
new = "  lastRenderKey=key;\n  transitionRender();\n"
if new not in html:
    if old not in html:
        raise SystemExit("v2.30 glitch hotfix: requestRender render call not found")
    html = html.replace(old, new, 1)

page.write_text(html, encoding="utf-8")
print("Applied v2.30 unmistakable viewport glitch transitions.")
