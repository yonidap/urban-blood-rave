from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
page = ROOT / "deployed" / "public" / "screen.html"
html = page.read_text(encoding="utf-8")

MARKER = "/* v2.31 cinematic blood-wash transitions */"
if MARKER in html:
    print("v2.31 blood-wash transitions already applied.")
    raise SystemExit(0)

# Remove older transition-only hotfixes if this script is ever re-run on an
# already-patched page. Render normally rebuilds from the clean v2.27 screen.
html = re.sub(
    r"\n\s*/\* v2\.(?:28|29|30)[^\n]*transitions \*/.*?(?=\n</style>)",
    "\n",
    html,
    flags=re.S,
)
html = re.sub(
    r"\n// v2\.(?:28|29|30)[^\n]*transition controller.*?(?=\n\nfunction userSelectingText)",
    "\n",
    html,
    flags=re.S,
)

css = r'''
    /* v2.31 cinematic blood-wash transitions */
    .blood-transition{position:fixed;inset:0;z-index:10000;overflow:hidden;pointer-events:none;visibility:hidden}
    .blood-transition.cover,.blood-transition.reveal{visibility:visible}
    .blood-sheet-svg{position:absolute;left:-2vw;top:-135vh;width:104vw;height:135vh;will-change:transform;backface-visibility:hidden;overflow:visible}
    .blood-transition.cover .blood-sheet-svg{animation:bloodCover .72s cubic-bezier(.43,.01,.18,1) forwards}
    .blood-transition.reveal .blood-sheet-svg{transform:translateY(124vh);animation:bloodReveal .64s cubic-bezier(.62,.02,.88,.58) forwards}
    .blood-grain{position:absolute;inset:0;opacity:0;background:repeating-linear-gradient(101deg,transparent 0 13px,rgba(255,255,255,.025) 13px 14px,transparent 14px 29px);mix-blend-mode:screen}
    .blood-transition.cover .blood-grain{animation:bloodGrainIn .72s ease forwards}
    .blood-transition.reveal .blood-grain{animation:bloodGrainOut .42s ease forwards}
    @keyframes bloodCover{0%{transform:translateY(0)}48%{transform:translateY(70vh)}72%{transform:translateY(99vh)}88%{transform:translateY(110vh)}100%{transform:translateY(124vh)}}
    @keyframes bloodReveal{0%{transform:translateY(124vh)}24%{transform:translateY(139vh)}100%{transform:translateY(262vh)}}
    @keyframes bloodGrainIn{0%,42%{opacity:0}68%{opacity:.17}100%{opacity:.07}}
    @keyframes bloodGrainOut{0%{opacity:.1}100%{opacity:0}}

    /* Correctly targets #screen; older glitch CSS accidentally targeted #root. */
    #screen.glitch-out{animation:ubrFallbackOut .16s steps(3,end) both}
    #screen.glitch-in{animation:ubrFallbackIn .28s steps(4,end) both}
    #screen.micro-glitch{animation:ubrMicroGlitch .14s steps(3,end) both}
    #screen.micro-glitch::after{content:"";position:fixed;inset:0;z-index:9999;pointer-events:none;background:linear-gradient(90deg,rgba(255,0,45,.10),transparent 40%,rgba(0,220,255,.08));mix-blend-mode:screen;animation:ubrMicroFlash .14s steps(2,end) both}
    @keyframes ubrFallbackOut{0%{transform:none;filter:none;opacity:1}35%{transform:translateX(-12px);filter:contrast(1.35)}70%{transform:translateX(9px);opacity:.72}100%{transform:translateX(-4px);opacity:.12}}
    @keyframes ubrFallbackIn{0%{transform:translateX(14px);filter:contrast(1.5);opacity:.15}24%{transform:translateX(-10px);opacity:.9}48%{transform:translateX(7px)}72%{transform:translateX(-3px)}100%{transform:none;filter:none;opacity:1}}
    @keyframes ubrMicroGlitch{0%,100%{transform:none;filter:none}20%{transform:translateX(-8px);filter:contrast(1.45)}46%{transform:translateX(7px);filter:hue-rotate(-7deg) contrast(1.35)}70%{transform:translateX(-3px)}86%{transform:translateX(2px)}}
    @keyframes ubrMicroFlash{0%,100%{opacity:0}24%{opacity:.9}50%{opacity:.2}72%{opacity:.65}}
'''
if "</style>" not in html:
    raise SystemExit("v2.31 blood hotfix: </style> not found")
html = html.replace("</style>", css + "\n</style>", 1)

overlay = r'''
<div id="bloodTransition" class="blood-transition" aria-hidden="true">
  <svg class="blood-sheet-svg" viewBox="0 0 1000 1350" preserveAspectRatio="none" aria-hidden="true">
    <defs>
      <linearGradient id="bloodBackGradient" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#170005"/><stop offset="58%" stop-color="#38000b"/><stop offset="100%" stop-color="#5d0012"/>
      </linearGradient>
      <linearGradient id="bloodMainGradient" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#280007"/><stop offset="48%" stop-color="#620012"/><stop offset="82%" stop-color="#98001d"/><stop offset="100%" stop-color="#52000f"/>
      </linearGradient>
      <linearGradient id="bloodSheen" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="#fff" stop-opacity="0"/><stop offset="18%" stop-color="#ff8897" stop-opacity=".08"/><stop offset="27%" stop-color="#fff" stop-opacity="0"/><stop offset="58%" stop-color="#ff9aa7" stop-opacity=".06"/><stop offset="66%" stop-color="#fff" stop-opacity="0"/><stop offset="88%" stop-color="#ff8192" stop-opacity=".06"/><stop offset="100%" stop-color="#fff" stop-opacity="0"/>
      </linearGradient>
      <filter id="bloodOrganic" x="-4%" y="-3%" width="108%" height="110%">
        <feTurbulence type="fractalNoise" baseFrequency="0.008 0.020" numOctaves="2" seed="21" result="noise"/>
        <feDisplacementMap in="SourceGraphic" in2="noise" scale="12" xChannelSelector="R" yChannelSelector="G"/>
      </filter>
    </defs>
    <path d="M0 0H1000V1115 C970 1132 955 1102 925 1150 C900 1190 875 1128 840 1162 C807 1194 790 1225 755 1172 C726 1128 700 1208 664 1170 C628 1132 612 1238 575 1180 C540 1128 520 1218 482 1172 C450 1134 430 1260 390 1182 C360 1126 330 1218 296 1170 C262 1124 240 1246 204 1180 C175 1128 145 1210 112 1164 C80 1120 50 1206 0 1160Z" fill="url(#bloodBackGradient)" opacity=".98"/>
    <path d="M0 0H1000V1142 C968 1164 952 1122 922 1180 C898 1228 873 1148 836 1190 C802 1228 787 1305 752 1202 C725 1145 695 1238 660 1195 C625 1153 610 1320 572 1210 C540 1148 515 1260 478 1200 C446 1150 425 1330 388 1212 C356 1148 327 1260 292 1198 C259 1142 236 1310 202 1208 C173 1148 142 1248 108 1190 C78 1140 48 1238 0 1180Z" fill="url(#bloodMainGradient)" filter="url(#bloodOrganic)"/>
    <g fill="#790016" opacity=".92" filter="url(#bloodOrganic)">
      <path d="M180 1184 C190 1202 194 1248 191 1300 C189 1337 176 1337 174 1299 C171 1250 173 1205 180 1184Z"/>
      <path d="M382 1205 C394 1225 397 1272 394 1336 C392 1362 378 1362 376 1332 C373 1271 376 1224 382 1205Z"/>
      <path d="M568 1202 C579 1222 582 1257 579 1315 C577 1348 564 1348 562 1313 C559 1260 562 1221 568 1202Z"/>
      <path d="M748 1197 C759 1215 763 1260 760 1324 C758 1355 744 1355 742 1320 C739 1260 742 1216 748 1197Z"/>
      <path d="M915 1178 C925 1195 929 1228 927 1280 C925 1311 912 1311 910 1278 C907 1230 909 1196 915 1178Z"/>
    </g>
    <path d="M0 0H1000V1142 C968 1164 952 1122 922 1180 C898 1228 873 1148 836 1190 C802 1228 787 1305 752 1202 C725 1145 695 1238 660 1195 C625 1153 610 1320 572 1210 C540 1148 515 1260 478 1200 C446 1150 425 1330 388 1212 C356 1148 327 1260 292 1198 C259 1142 236 1310 202 1208 C173 1148 142 1248 108 1190 C78 1140 48 1238 0 1180Z" fill="url(#bloodSheen)" opacity=".6"/>
  </svg>
  <div class="blood-grain"></div>
</div>
'''
if 'id="bloodTransition"' not in html:
    if "<script>" not in html:
        raise SystemExit("v2.31 blood hotfix: <script> anchor not found")
    html = html.replace("<script>", overlay + "\n<script>", 1)

js = r'''
// v2.31 cinematic blood-wash transition controller
const bloodOverlay=document.getElementById('bloodTransition');
const USE_BLOOD_TRANSITIONS=true; // one-switch fallback to glitch-only if desired
let transitionSeq=0,transitionTimer=null,transitionCleanup=null,lastSceneKind=null;
function clearTransitionClasses(){
  root.classList.remove('glitch-out','glitch-in','micro-glitch');
  bloodOverlay.classList.remove('cover','reveal');
}
function currentSceneKind(){
  if(!s)return'none';
  if(s.reveal)return'reveal';
  if(s.clue)return'clue';
  if(s.status==='finished')return'ending';
  if(s.status==='lobby')return'lobby';
  if(s.phase==='discussion')return'discussion';
  if(s.phase==='vote')return'vote';
  return'main';
}
function fallbackGlitchRender(){
  const seq=++transitionSeq;
  if(transitionTimer)clearTimeout(transitionTimer);
  if(transitionCleanup)clearTimeout(transitionCleanup);
  clearTransitionClasses();
  if(!root.firstElementChild){render();return}
  root.classList.add('glitch-out');
  transitionTimer=setTimeout(()=>{
    if(seq!==transitionSeq)return;
    root.classList.remove('glitch-out');
    render();
    void root.offsetWidth;
    root.classList.add('glitch-in');
    transitionCleanup=setTimeout(()=>{if(seq===transitionSeq)root.classList.remove('glitch-in')},300);
  },150);
}
function bloodWashRender(){
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
}
function transitionRender(){
  const nextKind=currentSceneKind();
  const previousKind=lastSceneKind;
  lastSceneKind=nextKind;
  if(!root.firstElementChild){render();return}
  if(previousKind===nextKind){render();return}
  const majorChange=previousKind!==null && previousKind!==nextKind;
  if(USE_BLOOD_TRANSITIONS && majorChange)bloodWashRender();
  else fallbackGlitchRender();
}
'''
anchor = "let socket;\n"
if anchor not in html:
    raise SystemExit("v2.31 blood hotfix: socket anchor not found")
html = html.replace(anchor, anchor + js + "\n", 1)

old = "  lastRenderKey=key;\n  render();\n"
new = "  lastRenderKey=key;\n  transitionRender();\n"
if new not in html:
    if old not in html:
        raise SystemExit("v2.31 blood hotfix: requestRender render call not found")
    html = html.replace(old, new, 1)

page.write_text(html, encoding="utf-8")
print("Applied v2.31 cinematic blood-wash scene transitions with corrected glitch fallback.")
