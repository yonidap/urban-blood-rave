from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent
page=ROOT/'deployed'/'public'/'screen.html'
html=page.read_text(encoding='utf-8')
MARK='/* v2.36 splash-then-drip pass */'
if MARK in html:
    print('v2.36 splash pass already applied.'); raise SystemExit(0)
if '/* v2.31 cinematic blood-wash transitions */' not in html:
    raise SystemExit('v2.36 splash pass: v2.31 baseline missing')

css=r'''/* v2.36 splash-then-drip pass */
    .blood-transition{position:fixed;inset:0;z-index:10000;overflow:hidden;pointer-events:none;visibility:hidden}
    .blood-transition.cover,.blood-transition.reveal{visibility:visible}
    .blood-splash-svg{position:absolute;left:-2vw;top:-3vh;width:104vw;height:58vh;opacity:0;transform:scale(.72) translateY(-5vh);transform-origin:50% 18%;will-change:transform,opacity}
    .blood-transition.cover .blood-splash-svg{animation:splashHit .23s cubic-bezier(.12,.78,.18,1) forwards,splashHold .54s .23s linear forwards}
    .blood-transition.reveal .blood-splash-svg{display:none}
    .blood-sheet-svg{position:absolute;left:-2vw;top:-142vh;width:104vw;height:142vh;opacity:0;will-change:transform;backface-visibility:hidden;overflow:visible}
    .blood-transition.cover .blood-sheet-svg{animation:sheetIn .66s .15s cubic-bezier(.39,.01,.16,1) forwards}
    .blood-transition.reveal .blood-sheet-svg{opacity:1;transform:translateY(130vh);animation:sheetOut .70s cubic-bezier(.58,.02,.88,.58) forwards}
    .blood-impact-flash{position:absolute;inset:0;opacity:0;background:radial-gradient(circle at 50% 18%,rgba(165,0,28,.25),rgba(24,0,5,.07) 36%,transparent 68%);mix-blend-mode:screen}
    .blood-transition.cover .blood-impact-flash{animation:impactFlash .30s ease-out forwards}
    .blood-transition.reveal .blood-impact-flash{display:none}
    .blood-grain{position:absolute;inset:0;opacity:0;background:repeating-linear-gradient(101deg,transparent 0 13px,rgba(255,255,255,.022) 13px 14px,transparent 14px 29px);mix-blend-mode:screen}
    .blood-transition.cover .blood-grain{animation:bloodGrainIn .8s ease forwards}.blood-transition.reveal .blood-grain{animation:bloodGrainOut .48s ease forwards}
    @keyframes splashHit{0%{opacity:0;transform:scale(.72) translateY(-5vh)}46%{opacity:1;transform:scale(1.045)}100%{opacity:1;transform:scale(1)}}
    @keyframes splashHold{0%,78%{opacity:1}100%{opacity:.82}}
    @keyframes sheetIn{0%{opacity:0;transform:translateY(0)}12%{opacity:1}42%{transform:translateY(62vh)}68%{transform:translateY(101vh)}88%{transform:translateY(119vh)}100%{opacity:1;transform:translateY(130vh)}}
    @keyframes sheetOut{0%{transform:translateY(130vh)}20%{transform:translateY(144vh)}100%{transform:translateY(278vh)}}
    @keyframes impactFlash{0%{opacity:0}35%{opacity:.78}100%{opacity:0}}
    @keyframes bloodGrainIn{0%,38%{opacity:0}62%{opacity:.13}100%{opacity:.05}}@keyframes bloodGrainOut{0%{opacity:.07}100%{opacity:0}}
'''
pat=r'/\* v2\.31 cinematic blood-wash transitions \*/.*?(?=\n\s*/\* Correctly targets #screen;)'
html,n=re.subn(pat,css,html,count=1,flags=re.S)
if n!=1: raise SystemExit('v2.36 splash pass: CSS block not replaced')

overlay=r'''<div id="bloodTransition" class="blood-transition" aria-hidden="true">
  <div class="blood-impact-flash"></div>
  <svg class="blood-splash-svg" viewBox="0 0 1200 620" preserveAspectRatio="none" aria-hidden="true">
    <defs><radialGradient id="splashCore" cx="50%" cy="26%" r="72%"><stop offset="0%" stop-color="#bc1731"/><stop offset="34%" stop-color="#8d0b22"/><stop offset="72%" stop-color="#520513"/><stop offset="100%" stop-color="#230006"/></radialGradient><filter id="splashOrganic" x="-8%" y="-10%" width="116%" height="125%"><feTurbulence type="fractalNoise" baseFrequency="0.012 0.024" numOctaves="2" seed="36" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="16"/></filter></defs>
    <g filter="url(#splashOrganic)" fill="url(#splashCore)"><path d="M-40 8H1240V98c-72-18-108 20-146 58-36 36-84 6-112-38-31-49-77-52-107 8-33 67-80 57-111 2-33-58-80-53-110 11-31 65-79 51-106-7-29-62-79-58-108 5-32 70-83 55-111-11-27-63-76-54-106 4-32 63-81 49-108-4-29-57-73-48-113-4L-40 144Z"/><path d="M78 104c17 62-2 126-27 181-16 35-4 70 21 52 27-21 32-78 44-129 8-34 23-61 46-69-23-27-50-40-84-35Z"/><path d="M260 104c20 60 12 138-13 211-16 46 0 87 29 57 31-33 28-94 39-155 6-38 21-67 43-77-27-30-59-41-98-36Z"/><path d="M500 110c20 54 16 125-7 189-15 41-5 86 23 58 30-29 32-88 42-149 5-34 20-59 41-69-29-28-63-38-99-29Z"/><path d="M744 108c24 60 15 138-8 218-14 45 3 87 33 53 30-35 26-98 38-162 7-38 22-66 45-77-29-30-68-41-108-32Z"/><path d="M1002 104c21 60 14 122-6 182-13 38 0 72 24 50 27-25 29-81 41-134 7-32 21-56 42-65-25-25-60-37-101-33Z"/></g>
    <g fill="#76091c"><ellipse cx="142" cy="392" rx="13" ry="20"/><ellipse cx="216" cy="330" rx="7" ry="11"/><ellipse cx="388" cy="415" rx="10" ry="16"/><ellipse cx="612" cy="365" rx="8" ry="13"/><ellipse cx="690" cy="442" rx="14" ry="22"/><ellipse cx="917" cy="352" rx="9" ry="15"/><ellipse cx="1082" cy="388" rx="12" ry="19"/></g>
  </svg>
  <svg class="blood-sheet-svg" viewBox="0 0 1000 1420" preserveAspectRatio="none" aria-hidden="true"><defs><linearGradient id="bloodMainGradient" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#210006"/><stop offset="45%" stop-color="#5b0817"/><stop offset="80%" stop-color="#930f25"/><stop offset="100%" stop-color="#3a020d"/></linearGradient><filter id="bloodOrganic" x="-5%" y="-4%" width="110%" height="112%"><feTurbulence type="fractalNoise" baseFrequency="0.008 0.019" numOctaves="2" seed="42" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="14"/></filter></defs><path d="M0 0H1000V1190c-30 24-54-28-86 36-24 46-53-35-88 8-33 42-48 131-82 16-27-65-56 44-92-12-36-58-53 146-92 24-32-78-60 58-96-15-31-65-56 155-92 19-32-86-61 60-97-26-31-72-58 132-93 10-29-70-57 57-91-23-28-62-56 45-91-7Z" fill="url(#bloodMainGradient)" filter="url(#bloodOrganic)"/></svg>
  <div class="blood-grain"></div>
</div>'''
html,n=re.subn(r'<div id="bloodTransition" class="blood-transition" aria-hidden="true">.*?</div>\n(?=<script>)',overlay+'\n',html,count=1,flags=re.S)
if n!=1: raise SystemExit('v2.36 splash pass: overlay not replaced')

html=html.replace('// v2.31 cinematic blood-wash transition controller','// v2.36 splash-then-drip blood transition controller',1)
old='''function bloodWashRender(){
  const seq=++transitionSeq;
  if(transitionTimer)clearTimeout(transitionTimer);
  if(transitionCleanup)clearTimeout(transitionCleanup);
  clearTransitionClasses();
  void bloodOverlay.offsetWidth;
  bloodOverlay.classList.add('cover');
  transitionTimer=setTimeout(()=>{
    if(seq!==transitionSeq)return;
    render();
    root.classList.add('micro-glitch');
    bloodOverlay.classList.remove('cover');
    void bloodOverlay.offsetWidth;
    bloodOverlay.classList.add('reveal');
    setTimeout(()=>{if(seq===transitionSeq)root.classList.remove('micro-glitch')},150);
    transitionCleanup=setTimeout(()=>{
      if(seq!==transitionSeq)return;
      bloodOverlay.classList.remove('reveal');
    },680);
  },700);
}'''
new='''function bloodSplashRender(){
  const seq=++transitionSeq;
  if(transitionTimer)clearTimeout(transitionTimer);
  if(transitionCleanup)clearTimeout(transitionCleanup);
  clearTransitionClasses();
  void bloodOverlay.offsetWidth;
  bloodOverlay.classList.add('cover');
  transitionTimer=setTimeout(()=>{
    if(seq!==transitionSeq)return;
    render();
    bloodOverlay.classList.remove('cover');
    void bloodOverlay.offsetWidth;
    bloodOverlay.classList.add('reveal');
    transitionCleanup=setTimeout(()=>{if(seq===transitionSeq)bloodOverlay.classList.remove('reveal')},735);
  },790);
}'''
if old not in html: raise SystemExit('v2.36 splash pass: old bloodWashRender not found')
html=html.replace(old,new,1).replace('bloodWashRender();','bloodSplashRender();',1)
page.write_text(html,encoding='utf-8')
print('Applied v2.36 splash-then-drip blood transition pass.')
