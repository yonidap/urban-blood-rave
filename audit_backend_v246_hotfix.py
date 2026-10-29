from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parent
app_path = ROOT / "deployed" / "app.py"
text = app_path.read_text(encoding="utf-8")
MARKER = "# v2.46 audit hardening"
if MARKER in text:
    print("v2.46 backend audit hardening already applied.")
    raise SystemExit(0)


def replace_function(source: str, name: str, replacement: str) -> str:
    tree = ast.parse(source)
    node = next((n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name), None)
    if not node:
        raise SystemExit(f"v2.46 backend: function {name} not found")
    lines = source.splitlines(keepends=True)
    start = node.lineno - 1
    end = node.end_lineno
    if end < len(lines) and lines[end].strip() == "":
        end += 1
    lines[start:end] = [replacement.rstrip() + "\n\n"]
    return "".join(lines)

scheduler = r'''async def scheduler_loop():
    # v2.46 audit hardening: scheduled gameplay events are only consumed after
    # they actually open. A temporary phase conflict therefore retries instead
    # of silently deleting the event. The loop also survives unexpected errors.
    while state['status'] == 'running':
        try:
            scheduler_health['lastTick'] = time.time()
            closed_window = False
            vote_due = False
            discussion_due = False
            sunrise_due = False
            async with state_lock:
                state['elapsedSec'] = max(0, int((time.time() - state['startedAt']) * time_scale()))
                due = []
                for at, typ, val in SCHEDULE:
                    key = f'{typ}:{at}:{val}'
                    if state['elapsedSec'] >= at and key not in state['fired']:
                        due.append((key, typ, val))
                w = state.get('activeBiteWindow')
                if w and now_ms() >= w['until']:
                    number = w['number']
                    log('bite-window-close', number=number)
                    state['activeBiteWindow'] = None
                    result = state.get('biteWindowResults', {}).setdefault(str(number), dict(converted=0, closed=False, summaryShown=False))
                    result['closed'] = True
                    closed_window = True
                    await maybe_finalize_bite_window(number)
                if state.get('votesOpen') and state.get('voteEndsAt') and now_ms() >= state['voteEndsAt']:
                    vote_due = True
                if state.get('discussionEndsAt') and not state.get('votesOpen') and now_ms() >= state['discussionEndsAt']:
                    discussion_due = True
                if state['elapsedSec'] >= GAME_DURATION_SEC and not state.get('votesOpen'):
                    sunrise_due = True

            if discussion_due:
                async with state_lock:
                    if state.get('discussionEndsAt') and now_ms() >= state['discussionEndsAt'] and not state.get('votesOpen'):
                        state['discussionEndsAt'] = None
                        if state.get('status') == 'running':
                            state['phase'] = 'running'

            if vote_due:
                async with state_lock:
                    await resolve_vote()

            for key, typ, val in due:
                if state.get('status') != 'running':
                    break
                async with state_lock:
                    if state.get('status') != 'running':
                        break
                    handled = True
                    if typ == 'clue':
                        await show_clue(val)
                    elif typ == 'bite_window':
                        handled = await open_bite_window(val)
                    elif typ == 'discussion':
                        handled = await start_discussion(val)
                    elif typ == 'vote':
                        handled = await open_vote(val)
                    elif typ == 'decoy':
                        # Decoys are cosmetic; even a no-candidate result should
                        # not spin forever once its scheduled moment has passed.
                        await send_decoy_alerts(val)
                        handled = True
                    if handled and key not in state['fired']:
                        state['fired'].append(key)
                    elif not handled:
                        log('scheduled-event-deferred', event=typ, value=val, elapsed=state.get('elapsedSec'))

            if sunrise_due and state.get('status') == 'running' and not state.get('votesOpen'):
                async with state_lock:
                    if state.get('status') == 'running' and not state.get('votesOpen'):
                        finish_game()

            await broadcast_all()
            scheduler_health['errors'] = 0
            scheduler_health['lastError'] = None
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            scheduler_health['errors'] = int(scheduler_health.get('errors', 0)) + 1
            scheduler_health['lastError'] = repr(exc)[:240]
            log('scheduler-error', detail=scheduler_health['lastError'], consecutive=scheduler_health['errors'])
            try:
                await broadcast_all()
            except Exception:
                pass
        await asyncio.sleep(0.25 if state.get('testMode') and time_scale() > 1 else 1.0)'''

text = replace_function(text, "scheduler_loop", scheduler)

# Do not allow a vote to leapfrog an active discussion, especially when a
# scheduled event was delayed by a temporary manual phase conflict.
old_vote_guard = "    if round_no in state.get('completedVoteRounds', []) or state.get('votesOpen') or state.get('activeBiteWindow'):\n        return False\n"
new_vote_guard = old_vote_guard + "    if state.get('discussionEndsAt') and now_ms() < state['discussionEndsAt']:\n        return False\n"
if old_vote_guard not in text:
    raise SystemExit("v2.46 backend: open_vote guard anchor not found")
text = text.replace(old_vote_guard, new_vote_guard, 1)

# Votes are final once cast. This matches the UI wording and prevents a player
# from repeatedly changing their vote until the last participant votes.
old_vote_target = "        if not target['alive'] or target['id'] == voter['id']:\n            raise HTTPException(400, 'invalid target')\n        voter['vote'] = target['id']\n"
new_vote_target = "        if voter.get('vote'):\n            raise HTTPException(409, 'vote already cast')\n        if not target['alive'] or target['id'] == voter['id']:\n            raise HTTPException(400, 'invalid target')\n        voter['vote'] = target['id']\n"
if old_vote_target not in text:
    raise SystemExit("v2.46 backend: vote assignment anchor not found")
text = text.replace(old_vote_target, new_vote_target, 1)

# A stale action notification is worse than no notification. Bite/vote windows
# are 90 seconds, so do not let Apple retain a push for five minutes.
text = text.replace("ttl=300,", "ttl=90,")

text += r'''

# v2.46 audit hardening
scheduler_health = {'lastTick': None, 'errors': 0, 'lastError': None}
player_presence = {}

@app.post('/api/player/{token}/presence')
async def player_presence_ping(token: str):
    p = get_player_by_token(token)
    if not p:
        raise HTTPException(404, 'invalid token')
    player_presence[p['id']] = time.time()
    return {'ok': True}

@app.get('/api/host/readiness')
async def host_readiness(key: str):
    if key != HOST_KEY:
        raise HTTPException(403, 'forbidden')
    now = time.time()
    rows = []
    for p in state['players']:
        last = player_presence.get(p['id'])
        rows.append({
            'id': p['id'],
            'name': p['name'],
            'alive': bool(p['alive']),
            'online': bool(last and now - last <= 45),
            'lastSeenSec': None if last is None else max(0, int(now - last)),
            'pushReady': bool(push_subscriptions.get(p['id'])),
        })
    tick = scheduler_health.get('lastTick')
    scheduler_age = None if tick is None else max(0.0, now - tick)
    scheduler_ok = state.get('status') != 'running' or bool(tick and scheduler_age < 5 and scheduler_health.get('errors', 0) < 3)
    return {
        'ok': True,
        'players': rows,
        'scheduler': {
            'ok': scheduler_ok,
            'ageSec': scheduler_age,
            'errors': scheduler_health.get('errors', 0),
            'lastError': scheduler_health.get('lastError'),
        },
    }
'''

app_path.write_text(text, encoding="utf-8")
print("Applied v2.46 backend audit hardening: scheduler retry/watchdog, final votes, readiness, TTL.")
