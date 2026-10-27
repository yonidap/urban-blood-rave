from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
app_path = ROOT / "deployed" / "app.py"
player_path = ROOT / "deployed" / "public" / "player.html"

app = app_path.read_text(encoding="utf-8")
player = player_path.read_text(encoding="utf-8")

APP_MARKER = "# v2.35 iOS Web Push reliability + diagnostics"
PLAYER_MARKER = "// v2.35 push self-test"

# Apple validates VAPID subjects more strictly than other push services. Use a
# real HTTPS contact URI instead of the old example.com placeholder.
app, subject_replacements = re.subn(
    r"VAPID_SUBJECT\s*=\s*os\.environ\.get\('VAPID_SUBJECT',\s*'mailto:urban-blood-rave@example\.com'\)",
    "VAPID_SUBJECT = os.environ.get('VAPID_SUBJECT', 'https://urban-blood-rave.onrender.com')",
    app,
    count=1,
)
if subject_replacements == 0 and "https://urban-blood-rave.onrender.com" not in app:
    raise SystemExit("v2.35 push hotfix: VAPID_SUBJECT anchor not found")

if APP_MARKER not in app:
    diagnostic_code = r'''

# v2.35 iOS Web Push reliability + diagnostics
# Override the earlier sender so all existing bite/vote/decoy callers pick up
# the corrected Apple-friendly VAPID subject plus delivery diagnostics.
push_delivery_status = {}

async def send_push_to_player(p, title, body, tag):
    subscriptions = list(push_subscriptions.get(p['id'], {}).items())
    if not subscriptions:
        push_delivery_status[p['id']] = {
            'ok': False,
            'status': 'no-subscription',
            'detail': 'No server-side push subscription is registered for this player.',
        }
        return push_delivery_status[p['id']]

    payload = json.dumps(dict(title=title, body=body, tag=tag, url=f"/p/{p['token']}"))
    stale = []
    results = []
    for endpoint, subscription in subscriptions:
        try:
            response = await asyncio.to_thread(
                webpush,
                subscription_info=subscription,
                data=payload,
                vapid_private_key=str(VAPID_PEM_PATH),
                vapid_claims={'sub': VAPID_SUBJECT},
                ttl=300,
                timeout=10,
                headers={'Urgency': 'high'},
            )
            status = int(getattr(response, 'status_code', 201) or 201)
            results.append({'ok': True, 'status': status})
            log('push-delivered', playerId=p['id'], status=status)
        except WebPushException as exc:
            response = getattr(exc, 'response', None)
            status = getattr(response, 'status_code', None)
            detail = ''
            try:
                detail = (getattr(response, 'text', '') or str(exc))[:240]
            except Exception:
                detail = str(exc)[:240]
            results.append({'ok': False, 'status': status or 'webpush-error', 'detail': detail})
            if status in (404, 410):
                stale.append(endpoint)
            log('push-error', playerId=p['id'], status=status or 'webpush-error', detail=detail)
        except Exception as exc:
            detail = repr(exc)[:240]
            results.append({'ok': False, 'status': 'exception', 'detail': detail})
            log('push-error', playerId=p['id'], status='exception', detail=detail)

    if stale:
        bucket = push_subscriptions.get(p['id'], {})
        for endpoint in stale:
            bucket.pop(endpoint, None)

    success = any(item.get('ok') for item in results)
    last = next((item for item in reversed(results) if not item.get('ok')), results[-1] if results else {'ok': False, 'status': 'unknown'})
    push_delivery_status[p['id']] = {
        'ok': success,
        'status': 201 if success else last.get('status', 'unknown'),
        'detail': '' if success else last.get('detail', ''),
        'subscriptions': len(subscriptions) - len(stale),
    }
    return push_delivery_status[p['id']]


@app.get('/api/player/{token}/push-status')
async def player_push_status(token: str):
    p = get_player_by_token(token)
    if not p:
        raise HTTPException(404, 'invalid token')
    return {
        'ok': True,
        'subscriptions': len(push_subscriptions.get(p['id'], {})),
        'last': push_delivery_status.get(p['id']),
        'vapidSubject': VAPID_SUBJECT,
    }


@app.post('/api/player/{token}/push-test')
async def player_push_test(token: str):
    p = get_player_by_token(token)
    if not p:
        raise HTTPException(404, 'invalid token')
    if not push_subscriptions.get(p['id']):
        return {
            'ok': False,
            'subscriptions': 0,
            'last': {'ok': False, 'status': 'no-subscription', 'detail': 'Enable alerts first.'},
        }
    result = await send_push_to_player(
        p,
        'URBAN BLOOD RAVE',
        'Test alert received. Push notifications are working.',
        'urban-blood-rave-push-test',
    )
    return {
        'ok': bool(result and result.get('ok')),
        'subscriptions': len(push_subscriptions.get(p['id'], {})),
        'last': result,
    }
'''
    app += diagnostic_code

if PLAYER_MARKER not in player:
    # Add a visible self-test next to the confirmed subscription state.
    subscribed_pattern = re.compile(
        r"if\(pushSubscribed\)\{\s*alertSetup\.innerHTML='<span>ACTION ALERTS ON</span>';return\s*\}",
        re.S,
    )
    subscribed_replacement = """if(pushSubscribed){\n    alertSetup.innerHTML='<span>ACTION ALERTS ON</span> <button class=\"notify-btn\" onclick=\"testAlert()\">TEST ALERT</button>';return\n  }"""
    player, n = subscribed_pattern.subn(subscribed_replacement, player, count=1)
    if n != 1:
        raise SystemExit("v2.35 push hotfix: ACTION ALERTS ON branch not found")

    anchor = "async function enableAlerts(){"
    if anchor not in player:
        raise SystemExit("v2.35 push hotfix: enableAlerts anchor not found")
    test_js = r'''
// v2.35 push self-test
async function testAlert(){
  alertSetup.innerHTML='<span>SENDING TEST ALERT…</span>';
  try{
    const r=await fetch(`/api/player/${token}/push-test`,{method:'POST',cache:'no-store'});
    const j=await r.json();
    const last=j.last||{};
    if(r.ok&&j.ok){
      alertSetup.innerHTML='<span>TEST SENT · CHECK NOTIFICATIONS</span>';
      setTimeout(renderAlertSetup,3500);
      return;
    }
    const status=last.status||r.status||'ERROR';
    let detail=(last.detail||'').replace(/<[^>]+>/g,'').trim();
    if(detail.length>72)detail=detail.slice(0,72)+'…';
    alertSetup.innerHTML=`<span>PUSH ERROR · ${status}${detail?' · '+detail:''}</span>`;
    setTimeout(renderAlertSetup,7000);
  }catch(e){
    alertSetup.innerHTML='<span>PUSH TEST FAILED</span>';
    setTimeout(renderAlertSetup,5000);
  }
}

'''
    player = player.replace(anchor, test_js + anchor, 1)

app_path.write_text(app, encoding="utf-8")
player_path.write_text(player, encoding="utf-8")
print("Applied v2.35 iOS Web Push reliability fix and self-test diagnostics.")
