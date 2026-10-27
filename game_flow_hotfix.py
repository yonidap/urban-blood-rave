from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
app = ROOT / "deployed" / "app.py"
text = app.read_text(encoding="utf-8")

MARKER = "# v2.28 flow hotfix: defer decoys during clues"
if MARKER not in text:
    # 1) Defer the entire decoy delivery while a clue takeover is active.
    needle = "async def send_decoy_alerts(event_no):\n"
    if needle not in text:
        raise SystemExit("v2.28 flow hotfix: send_decoy_alerts not found")
    text = text.replace(
        needle,
        needle
        + f"    {MARKER}\n"
        + "    if state.get('activeClueIndex') is not None:\n"
        + "        pending = state.setdefault('pendingDecoyEvents', [])\n"
        + "        if event_no not in pending:\n"
        + "            pending.append(event_no)\n"
        + "            log('decoy-deferred', event=event_no)\n"
        + "        return True\n",
        1,
    )

    # 2) Once the clue has fully cleared, deliver deferred decoys in FIFO order.
    m = re.search(r"async def clear_clue_after\(session_id, index, until\):\n(?P<body>.*?)(?=\ndef mark_scheduled_event_fired)", text, re.S)
    if not m:
        raise SystemExit("v2.28 flow hotfix: clear_clue_after block not found")
    block = m.group(0)
    if "pendingDecoyEvents" not in block:
        tail = "    await broadcast_all()\n"
        pos = block.rfind(tail)
        if pos < 0:
            raise SystemExit("v2.28 flow hotfix: clear_clue_after broadcast tail not found")
        replacement = (
            "    await broadcast_all()\n"
            "    # A decoy that landed during the clue is delivered only after the\n"
            "    # clue takeover has disappeared, so CHECK YOUR PHONES never competes\n"
            "    # visually with the clue and the private alert gets its full lifetime.\n"
            "    if state.get('activeClueIndex') is None:\n"
            "        deferred = list(state.pop('pendingDecoyEvents', []) or [])\n"
            "        for event_no in deferred:\n"
            "            await send_decoy_alerts(event_no)\n"
        )
        block = block[:pos] + replacement + block[pos+len(tail):]
        text = text[:m.start()] + block + text[m.end():]

    # 3) Don't show CHECK YOUR PHONES for a bite window unless at least one
    # original vampire can actually act and there is at least one valid target.
    m = re.search(r"async def open_bite_window\(number\):\n(?P<body>.*?)(?=\n\nasync def start_discussion)", text, re.S)
    if not m:
        raise SystemExit("v2.28 flow hotfix: open_bite_window block not found")
    block = m.group(0)
    cue = "    trigger_phone_cue()\n"
    if cue in block and "bite_cue_recipients" not in block:
        conditional = (
            "    bite_cue_recipients = [\n"
            "        p for p in original_vampires()\n"
            "        if p['alive'] and p['bitesRemaining'] > 0\n"
            "        and number not in p['biteWindowsUsed'] and p['id'] not in pending_bites\n"
            "    ]\n"
            "    bite_cue_targets = [\n"
            "        p for p in alive_players()\n"
            "        if p['currentRole'] == 'human' and not p['scarred']\n"
            "    ]\n"
            "    if bite_cue_recipients and bite_cue_targets:\n"
            "        trigger_phone_cue()\n"
        )
        block = block.replace(cue, conditional, 1)
        text = text[:m.start()] + block + text[m.end():]

app.write_text(text, encoding="utf-8")
print("Applied v2.28 flow hotfix: clue-safe decoys + bite cue eligibility.")
