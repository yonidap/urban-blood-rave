import os
import sys
import time
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
DEPLOYED = ROOT / "deployed"
sys.path.insert(0, str(DEPLOYED))
os.environ.setdefault("HOST_KEY", "ci-host-key")

import app as game  # noqa: E402

KEY = "ci-host-key"


def host_state(client):
    r = client.get("/api/host/state", params={"key": KEY})
    assert r.status_code == 200, r.text
    return r.json()


def post_host(client, path, json=None):
    r = client.post(path, params={"key": KEY}, json=json)
    assert r.status_code == 200, f"{path}: {r.status_code} {r.text}"
    return r.json()


def wait_until(predicate, timeout=8.0, interval=0.05, message="condition"):
    end = time.time() + timeout
    last = None
    while time.time() < end:
        last = predicate()
        if last:
            return last
        time.sleep(interval)
    raise AssertionError(f"Timed out waiting for {message}; last={last!r}")


def configure_speed(client, speed):
    r = client.post(
        "/api/host/test-config",
        params={"key": KEY},
        json={"enabled": True, "speed": speed},
    )
    assert r.status_code == 200, r.text


def reset(client):
    post_host(client, "/api/host/reset")


def test_scheduler_retries_blocked_event_and_preserves_discussion_duration():
    """Regression for the audit finding: a temporarily blocked scheduled event
    must remain pending instead of being consumed forever.
    """
    with TestClient(game.app) as client:
        reset(client)
        configure_speed(client, 60)
        post_host(client, "/api/host/start")

        earlier = [f"{typ}:{at}:{val}" for at, typ, val in game.SCHEDULE if at < 810]
        game.state["fired"] = earlier
        game.state["startedAt"] = time.time() - (805 / game.time_scale())

        post_host(client, "/api/host/bite-window/2")
        discussion_key = "discussion:810:1"
        vote_key = "vote:900:1"

        wait_until(lambda: game.state.get("elapsedSec", 0) >= 812, timeout=2, message="discussion due")
        assert discussion_key not in game.state["fired"]
        assert game.state.get("activeBiteWindow") is not None

        wait_until(
            lambda: game.state.get("phase") == "discussion" and discussion_key in game.state["fired"],
            timeout=4,
            message="retried discussion",
        )
        discussion_until = game.state["discussionEndsAt"]
        assert discussion_until and discussion_until > game.now_ms()

        wait_until(lambda: game.state.get("elapsedSec", 0) >= 902, timeout=3, message="vote absolute due")
        assert not game.state["votesOpen"]
        assert vote_key not in game.state["fired"]

        wait_until(lambda: game.state["votesOpen"] and vote_key in game.state["fired"], timeout=4, message="vote after discussion")
        reset(client)


def test_full_game_all_players_participate_end_to_end():
    """A complete accelerated match through the real HTTP API and scheduler.

    The full audit runs at 15x rather than 60x because protected-player Scar
    videos intentionally remain on the public screen for at least 12 real
    seconds. At 60x four Scar videos alone take longer than the entire 46.5 s
    match, so a 60x run cannot honestly validate that every scheduled visual
    event was actually published before the final vote.

    Scenario:
      W1: Shalev→Gal (scar), Ellen→Dan (convert), Yonatan→Yakir (scar)
      W2: Shalev→Tal (second failed bite => dies), Ellen→Ori (scar),
          Yonatan→Maor (convert)
      W3: no original has bites remaining
      Votes eliminate Rafael, Lutz, Kiso; every living player votes each round.
    """
    with TestClient(game.app) as client:
        reset(client)
        configure_speed(client, 15)
        hs = host_state(client)
        players = {p["id"]: p for p in hs["players"]}
        assert len(players) == 13

        for p in players.values():
            r = client.post(f"/api/player/{p['token']}/presence")
            assert r.status_code == 200, r.text
        ready = client.get("/api/host/readiness", params={"key": KEY})
        assert ready.status_code == 200
        ready_json = ready.json()
        assert len(ready_json["players"]) == 13
        assert all(p["online"] for p in ready_json["players"])

        post_host(client, "/api/host/start")

        bite_plan = {
            1: {"shalev": "gal", "alan": "dan", "yonatan": "yakir"},
            2: {"shalev": "tal", "alan": "uri", "yonatan": "maor"},
        }
        vote_targets = {1: "rafael", 2: "lutz", 3: "kiso"}
        bites_sent = set()
        votes_sent = set()
        vote_participation = {1: set(), 2: set(), 3: set()}
        last_presence = 0.0
        deadline = time.time() + 230

        while time.time() < deadline:
            hs = host_state(client)
            if hs["status"] == "finished":
                break

            if time.time() - last_presence > 10:
                for p in hs["players"]:
                    if p.get("alive", True):
                        client.post(f"/api/player/{p['token']}/presence")
                last_presence = time.time()

            bw = hs.get("biteWindow") or hs.get("activeBiteWindow")
            if bw:
                number = int(bw["number"])
                for vamp_id, target_id in bite_plan.get(number, {}).items():
                    marker = (number, vamp_id)
                    if marker in bites_sent:
                        continue
                    current = {p["id"]: p for p in hs["players"]}
                    vamp = current[vamp_id]
                    target = current[target_id]
                    if not vamp.get("alive", True) or vamp.get("bitesRemaining", 0) <= 0:
                        continue
                    r = client.post(
                        f"/api/player/{vamp['token']}/bite",
                        json={"targetId": target["id"]},
                    )
                    assert r.status_code == 200, f"bite {marker}: {r.status_code} {r.text}"
                    bites_sent.add(marker)

            if hs.get("votesOpen"):
                round_no = int(hs["currentRound"])
                target_id = vote_targets[round_no]
                alive = [p for p in hs["players"] if p.get("alive", True)]
                for voter in alive:
                    marker = (round_no, voter["id"])
                    if marker in votes_sent:
                        continue
                    choice = target_id
                    if voter["id"] == choice:
                        choice = next(
                            p["id"] for p in alive
                            if p["id"] != voter["id"] and p["id"] != target_id
                        )
                    r = client.post(
                        f"/api/player/{voter['token']}/vote",
                        json={"targetId": choice},
                    )
                    assert r.status_code == 200, f"vote {marker}: {r.status_code} {r.text}"
                    votes_sent.add(marker)
                    vote_participation[round_no].add(voter["id"])

            time.sleep(0.04)
        else:
            raise AssertionError("Full game did not finish within 230 real seconds at 15x")

        final = host_state(client)
        assert final["status"] == "finished"
        assert final["winner"]["side"] == "humans"

        assert sorted(game.state["completedVoteRounds"]) == [1, 2, 3]
        assert sorted(game.state["publishedClues"]) == [0, 1, 2, 3, 4, 5]

        internal = {p["id"]: p for p in game.state["players"]}
        assert {p["playerId"] for p in game.state["scarLoop"]} == {"gal", "yakir", "tal", "uri"}
        assert all(internal[p]["scarred"] for p in ("gal", "yakir", "tal", "uri"))
        assert internal["dan"]["currentRole"] == "converted"
        assert internal["maor"]["currentRole"] == "converted"
        assert internal["shalev"]["alive"] is False
        assert internal["shalev"]["failedBites"] == 2
        assert internal["rafael"]["alive"] is False
        assert internal["lutz"]["alive"] is False
        assert internal["kiso"]["alive"] is False

        assert bites_sent == {
            (1, "shalev"), (1, "alan"), (1, "yonatan"),
            (2, "shalev"), (2, "alan"), (2, "yonatan"),
        }
        assert len(vote_participation[1]) == 13
        assert len(vote_participation[2]) == 11
        assert len(vote_participation[3]) == 10

        assert game.scheduler_health["errors"] == 0, game.scheduler_health
        expected_fired = {f"{typ}:{at}:{val}" for at, typ, val in game.SCHEDULE}
        assert expected_fired.issubset(set(game.state["fired"]))


def test_v246_safety_surfaces_are_in_built_artifacts():
    player = (DEPLOYED / "public" / "player.html").read_text(encoding="utf-8")
    host = (DEPLOYED / "public" / "host.html").read_text(encoding="utf-8")
    screen = (DEPLOYED / "public" / "screen.html").read_text(encoding="utf-8")
    app_source = (DEPLOYED / "app.py").read_text(encoding="utf-8")
    build = (DEPLOYED / "public" / "build.txt").read_text(encoding="utf-8").strip()

    assert build == "v2.46"
    assert "v2.46 audit hardening" in app_source
    assert "ttl=90" in app_source
    assert "vote already cast" in app_source
    assert "/api/host/readiness" in app_source
    assert "v2.46 player safety + presence" in player
    assert "TEST ALERT" in player and "st?.status==='lobby'" in player
    assert "ADVANCED MANUAL OVERRIDES" in host
    assert "FINAL CONFIRMATION: reset now?" in host
    assert "Preflight" in host
    assert "v2.46 screen connectivity watchdog" in screen
