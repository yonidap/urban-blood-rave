# Urban Blood Rave — v2.20 audited build

Browser-based party game for 13 players + one public main screen + host dashboard.

## Run

```bash
python3 -m pip install -r requirements.txt
HOST_KEY=my-secret python3 -m uvicorn app:app --host 0.0.0.0 --port 3000
```

Open:
- Main screen: `http://localhost:3000/screen`
- Host: `http://localhost:3000/host?key=my-secret`
- The Host dashboard now detects the computer LAN IP and displays shareable phone links even when the Host itself was opened through `localhost`.

For the party, keep the computer and phones on the same Wi-Fi. Personal links are stable across RESET and server restarts.

## Rules implemented

- Original Vampires: Shalev, Ellen, Yonatan.
- Protected Humans: Gal, Yakir, Tal, Ori. Their protection is hidden from them until they survive a bite.
- Only Original Vampires can bite.
- Each Original Vampire has 2 bite attempts total.
- Bite windows: 07:00, 22:00, 37:00; each lasts 90 seconds.
- Each Original Vampire can bite at most once per bite window.
- A Human already selected by another pending bite is temporarily unavailable to other Vampires, preventing duplicate wasted bites.
- A scarred/confirmed Human is no longer offered as a bite target.
- Protected bite => BITE REJECTED / SCARRED + one failed bite for the Vampire.
- 2 failed bites kill the Original Vampire immediately; the public death reveal is queued after the scar reveal.
- Unprotected bite => CONVERTED; joins the Vampire side but cannot bite.
- Conversions are summarized once at the end of each bite window as BLOODLINE EXPANDED. Protected bite reveals remain individual.
- Vampire-side players can see all other living Vampires and whether they are ORIGINAL or CONVERTED.

## Timeline

- Clues: 05:00, 10:00, 20:00, 25:00, 35:00, 40:00.
- Each clue takes over the main screen for exactly 20 seconds and then stays in the revealed clue list.
- Discussions: 13:30, 28:30, 43:30; each lasts 90 seconds.
- Votes: 15:00, 30:00, 45:00; each lasts up to 90 seconds.
- A vote resolves early if every living player has voted; otherwise it auto-resolves at the deadline.
- Round 3 is shown as FINAL VOTE.
- Sunrise/game deadline is 46:30 so the final 90-second vote happens before the countdown reaches zero.

## Vote / reveal

- Every living player votes, including Vampires and Converted players.
- Highest vote total is eliminated. A tie currently eliminates nobody.
- Reveal sequence: CHOSEN -> player name -> burn effect -> HUMAN / CONVERTED / VAMPIRE.
- Main-screen live events use a FIFO queue so reveals never overwrite one another.

## Win conditions

The game can end early:
- HUMANS WIN immediately if every Original Vampire is dead.
- VAMPIRES WIN immediately if living Vampires (Original + Converted) reach or exceed living Humans.
- If neither side has triggered an early win by the end of the final vote / sunrise, HUMANS WIN.

The end screen reveals the winning side, final counts, and the Original Vampires.

## Scar media

Put bite animations here:
- `public/scars/gal.mp4`
- `public/scars/yakir.mp4`
- `public/scars/tal.mp4`
- `public/scars/uri.mp4`

During the bite event, the video is played. Afterwards, the main screen keeps a compact gallery of every Scarred Human using the final frame of each video as a persistent confirmed-human portrait.

## Reliability / UX safeguards

- Host/player/main-screen views update live via WebSockets with polling fallback.
- Re-rendering is minimized so text selection, vote taps, and bite target selection are not interrupted by timer updates.
- Scheduled clues, bite windows, discussions, and votes are marked as consumed when triggered manually, so they do not fire again at their original scheduled time.
- START is only accepted from the lobby; RESET is required before a new match.
- Manual controls are rejected when they would overlap an incompatible active phase.
- Stale reveal/clue timers from a previous RESET cannot modify the new match.

## Notifications

On local HTTP Wi-Fi, true background Web Push is not reliable on mobile browsers. While the player page is open, action alerts arrive live via WebSocket with in-app alert, vibration/audio, and browser notification where allowed. HTTPS/PWA deployment would be required for reliable background push.

## Remaining intentional limitation

- Game state is in memory. Restarting the server resets the current match (personal links stay stable).
- A tied vote currently produces no elimination; there is no runoff vote.

## Test Mode

The Host page now includes a Test Mode panel available while the game is in the lobby.

1. Enable **Test Mode**.
2. Choose any speed from **1x to 60x**.
3. Click **APPLY**.
4. Start the game normally.

The multiplier accelerates the entire game timeline consistently: scheduled clues, bite windows, bite-resolution delays, discussions, votes, reveals, and sunrise. For example, at 10x a 90-second vote lasts 9 real seconds and a 20-second clue lasts 2 real seconds.

For consistency, speed is locked after START. Use RESET to return to the lobby and choose a different speed.

## v2.24 additions
- Main screen shows **CHECK YOUR PHONES** for 8 game-seconds whenever a phone action opens (bite window or vote), and during decoy-alert bursts.
- Living humans receive harmless private vampire-lore decoy alerts at scattered times throughout the game to camouflage phone-checking behavior.
- Decoy alerts end with **DON'T TELL ANYONE.** and have no gameplay effect.
- Fire reveal WebM is served from `/static/fire_overlay.webm`.
