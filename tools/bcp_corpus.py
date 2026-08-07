#!/usr/bin/env python3
"""bcp_corpus.py — build a training corpus of REAL games from many BCP events (public data only).

Enumerates 40k events in a date range (the /play/events search, API-side), filters to real matched-play
GTs (>= min rounds / players), and pulls each event's PUBLIC roster (faction + Force Disposition) + pairings
(who beat whom). No token, no decklist fetch. Emits one row per DECIDED game:
    {event, p1_fac, p1_disp, p2_fac, p2_disp, p1_pts, p2_pts, p1_won}
-> data/bcp/corpus/games.json  (the training set for tools/bcp_predict.py).

  python3 tools/bcp_corpus.py [--start 2026-07-27] [--end 2026-08-31] [--min-rounds 5] [--min-players 32]
"""
import json, os, sys, time, urllib.parse, urllib.request, argparse

BASE = "https://newprod-api.bestcoastpairings.com/v1"
H = {"User-Agent": "Mozilla/5.0", "client-id": "web-app", "Accept": "application/json"}
FORTK = "WGMSzfKFYA"          # Warhammer 40,000 gameSystemId


def _get(path, params):
    url = BASE + "/" + path + "?" + urllib.parse.urlencode(params, doseq=True)
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=30))


def _paged(path, params, keyfn):
    acc, cur, seen = {}, None, set()
    while True:
        p = list(params) + ([("nextKey", cur)] if cur else [])
        d = _get(path, p)
        for r in d.get("data", []):
            acc[keyfn(r)] = r
        nk = d.get("nextKey")
        if not d.get("data") or not nk or nk in seen:
            break
        seen.add(nk); cur = nk; time.sleep(0.05)
    return list(acc.values())


def _nm(u):
    return " ".join(x for x in ((u or {}).get("firstName"), (u or {}).get("lastName")) if x).strip()


def enumerate_events(start, end, min_rounds, min_players):
    evs = _paged("events", [("startDate", start), ("endDate", end), ("gameSystemId", FORTK),
                            ("sortKey", "eventDate"), ("sortAsc", "true"), ("limit", 100)], lambda e: e["id"])
    out = []
    for e in evs:
        if (e.get("numberOfRounds") or 0) >= min_rounds and (e.get("totalPlayers") or 0) >= min_players:
            out.append(e)
    return out


def pull_event(eid):
    # NOTE: faction + team come by DEFAULT; expanding faction BLANKS it (bcp_pull.py). Only expand
    # user + subFaction (subFaction = the Force Disposition).
    players = _paged("players", [("eventId", eid), ("limit", 99), ("expand[]", "user"),
                                 ("expand[]", "subFaction")], lambda r: r["id"])
    info = {}
    for r in players:
        nm = _nm(r.get("user"))
        fac = (r.get("faction") or {}).get("name") if isinstance(r.get("faction"), dict) else r.get("faction")
        disp = (r.get("subFaction") or {}).get("name") if isinstance(r.get("subFaction"), dict) else r.get("subFactionName")
        if nm:
            info[nm] = (fac, disp)
    games = []
    for rnd in range(1, 7):
        pr = _paged("pairings", [("eventId", eid), ("round", rnd), ("pairingType", "Pairing"),
                                 ("limit", 99), ("expand[]", "player1"), ("expand[]", "player2"),
                                 ("expand[]", "player1Game"), ("expand[]", "player2Game")], lambda r: r["id"])
        for x in pr:
            p1, p2 = _nm(x.get("player1")), _nm(x.get("player2"))
            g1 = (x.get("player1Game") or {}).get("gamePoints")
            g2 = (x.get("player2Game") or {}).get("gamePoints")
            if p1 in info and p2 in info and g1 is not None and g2 is not None and g1 != g2:
                f1, d1 = info[p1]; f2, d2 = info[p2]
                if f1 and f2:
                    games.append(dict(p1_fac=f1, p1_disp=d1, p2_fac=f2, p2_disp=d2,
                                      p1_pts=g1, p2_pts=g2, p1_won=g1 > g2))
    return games


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2026-07-27"); ap.add_argument("--end", default="2026-08-31")
    # data hygiene: >=5 rounds + >=28 players — smaller events are skewed by local metas. And only games
    # from the current balance (post-latest-dataslate; 11E launch 2026-07-27, no dataslate since).
    ap.add_argument("--min-rounds", type=int, default=5); ap.add_argument("--min-players", type=int, default=28)
    a = ap.parse_args()
    evs = enumerate_events(a.start, a.end, a.min_rounds, a.min_players)
    print(f"# {len(evs)} matching 40k GTs ({a.min_rounds}+ rounds, {a.min_players}+ players, {a.start}..{a.end})",
          flush=True)
    allg = []
    for i, e in enumerate(evs):
        try:
            g = pull_event(e["id"])
            allg += g
            print(f"  [{i+1}/{len(evs)}] {(e.get('name') or '')[:38]:38} {e.get('totalPlayers'):>3}p  +{len(g)} games "
                  f"(total {len(allg)})", flush=True)
        except Exception as ex:
            print(f"  [{i+1}/{len(evs)}] {(e.get('name') or '')[:38]:38} ERR {str(ex)[:40]}", flush=True)
        time.sleep(0.1)
    os.makedirs("data/bcp/corpus", exist_ok=True)
    json.dump({"events": len(evs), "games": allg}, open("data/bcp/corpus/games.json", "w"))
    print(f"\n# wrote data/bcp/corpus/games.json — {len(allg)} decided games from {len(evs)} events")


if __name__ == "__main__":
    main()
