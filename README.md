# Urban Blood Rave — v2.46 audited build

Browser-based Halloween party game for 13 players, one public TV screen and a host console.

## Build and run

The repository is currently assembled through `bootstrap.py`: it reconstructs the deployed application and applies the production hotfixes in the same order used by Render.

```bash
python3 bootstrap.py
python3 -m pip install -r deployed/requirements.txt
cd deployed
HOST_KEY=my-secret python3 -m uvicorn app:app --host 0.0.0.0 --port 3000
```

Open:
- Main screen: `http://localhost:3000/screen`
- Host: `http://localhost:3000/host?key=my-secret`
- Players: use the personal links shown by the Host console.

Production is deployed as an HTTPS PWA. The public screen supports `?debug=1` to show the deployed build version.

## Roles and bite rules

- Original Vampires: Shalev, Ellen, Yonatan.
- Protected Humans: Gal, Yakir, Tal, Ori. Protection is hidden until they survive a bite.
- Only Original Vampires can bite; Converted players cannot bite.
- Each Original Vampire has 2 bite attempts total and at most 1 bite per Bite Window.
- Bite Windows: 07:00, 22:00, 37:00; each lasts 90 seconds.
- A pending target is unavailable to another Vampire, preventing duplicate wasted bites.
- A scarred/confirmed Human cannot be targeted again.
- Protected bite => BITE REJECTED / SCARRED + one failed bite for that Vampire.
- Two failed protected bites kill the Original Vampire.
- Unprotected bite => CONVERTED and joins the Vampire side.
- Conversions from one Bite Window are summarized as BLOODLINE EXPANDED after all pending bite outcomes in that window resolve.
- Win conditions are evaluated after the current Bite Window's pending bite outcomes have finished, so results from one window behave as a single batch.

## Timeline

- Clues: 05:00, 10:00, 20:00, 25:00, 35:00, 40:00.
- Bite Windows: 07:00, 22:00, 37:00.
- Discussions: 13:30, 28:30, 43:30; each lasts 90 seconds.
- Votes: 15:00, 30:00, 45:00; each lasts up to 90 seconds.
- Round 3 is FINAL VOTE.
- Sunrise/game deadline: 46:30.
- Decoy private alerts are scattered through the timeline to camouflage real phone actions.

If a scheduled Bite/Discussion/Vote is temporarily blocked by another phase, the scheduler now leaves it pending and retries instead of silently consuming it. A delayed vote cannot leapfrog a still-active 90-second discussion.

## Voting

- Every living player votes, including Original Vampires and Converted players.
- Self-voting is rejected.
- A vote is final after the first successful cast and cannot be changed.
- If every living player votes, the round resolves immediately; otherwise it resolves at the deadline.
- Highest vote total is eliminated.
- A tie eliminates nobody; there is no runoff.
- Reveal sequence: CHOSEN -> player name -> burn/reveal -> HUMAN / CONVERTED / VAMPIRE.
- Main-screen reveals use a FIFO queue so live events do not overwrite one another.

## Win conditions

- HUMANS WIN if all Original Vampires are dead.
- VAMPIRES WIN if living Vampires (Original + Converted) reach or exceed living Humans.
- If neither early condition has fired by the end of the final vote / sunrise, HUMANS WIN.

## Scar media

Protected-player bite animations:
- `public/scars/gal.mp4`
- `public/scars/yakir.mp4`
- `public/scars/tal.mp4`
- `public/scars/ori.mp4`

The public screen chroma-keys the animation background at runtime. Yakir uses a dedicated black-key path; the others use green-key processing. Tal's reveal starts about 1.05 seconds into the source clip. The finished Scarred players remain in the TV gallery after the reveal.

## Notifications / PWA

- iPhone players should install the HTTPS site to the Home Screen and enable action alerts.
- Web Push uses VAPID and the production HTTPS origin.
- All lock-screen Push payloads are intentionally privacy-safe: the visible notification text is simply `NOTIFICATION`.
- Push TTL is 90 seconds so an action notification should not arrive several minutes after its window has ended.
- Push is used for Bite opportunities, voting and decoy alerts.
- TEST ALERT is available only in the lobby.
- The Host preflight panel shows each player's current ONLINE and PUSH readiness.

## Player privacy

- Before START, the personal page shows only ROLE PREVIEW until the player explicitly reveals it.
- During the game, role/mission/team information is hidden by default and can be revealed for 5 seconds.
- Moving the PWA to the background immediately returns the page to the hidden identity state.
- Player and public screens display RECONNECTING only after repeated connectivity failures.

## Host safety

- START warns if one or more players are offline or do not have Push ready.
- RESET requires two explicit confirmations.
- RESOLVE VOTE warns if living players have not all voted.
- Spoiler-heavy role state is collapsed by default.
- Manual recovery controls are under ADVANCED MANUAL OVERRIDES and are disabled while a Bite Window, discussion or vote is active.
- Scheduler health is exposed in the preflight panel.

## Test Mode and automated audit

Test Mode is available in the lobby at 1x–60x. Speed is locked after START; RESET returns to the lobby.

GitHub Actions rebuilds `deployed/` exactly through `bootstrap.py`, compiles the Python application and runs `tests/test_full_game.py` on every push to `main`.

The integration suite includes:
- a scheduler regression test that deliberately overlaps a manual Bite Window with a scheduled Discussion and verifies the Discussion is retried and the Vote still waits for its full discussion;
- a full 60x match in which all 13 player clients report presence, Original Vampires submit bites through their personal endpoints, all living players vote in all three rounds, all six clues and all three Bite Windows run, four protected players are Scarred, humans are Converted, an Original Vampire dies after two failed bites, and the match reaches a verified final winner;
- static assertions that the v2.46 safety/readiness/privacy changes are present in the generated production artifacts.

## Intentional operational limitation

Current game state and Push subscriptions live in process memory. A Render process restart during a live match resets the match and loses server-side Push subscriptions. This is intentionally not being migrated to a persistent store immediately before the party; a future clean rebuild should make persistence and the repository source structure first-class rather than continuing the historical hotfix chain.
