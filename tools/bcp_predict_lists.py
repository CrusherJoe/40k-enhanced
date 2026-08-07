#!/usr/bin/env python3
"""bcp_predict_lists.py — does LIST COMPOSITION (which units are in the army) predict wins?

Baseline (bcp_predict) showed faction+disposition are ~non-predictive (AUC ~0.50). The real signal, if any,
is at the list level. This uses the events for which we have FULL army lists in the DB (units table) and
tests whether a bag-of-units model beats faction-only — and prints the per-unit win-correlation, which is
the substrate for change-RECOMMENDATIONS ("winning lists run more X, less Y").

Features are ANTISYMMETRIC (each game added both ways). Bag-of-units restricted to units appearing in >=
MIN_LISTS armies (drop noise). Cross-validated AUC; per-unit learned weights.

  PYTHONPATH=src python3 tools/bcp_predict_lists.py [events] [--l2 3] [--min-lists 8]
"""
import sys, os, json, sqlite3, argparse, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import numpy as np


def auc(scores, labels):
    pos = np.array([s for s, l in zip(scores, labels) if l], float)
    neg = np.array([s for s, l in zip(scores, labels) if not l], float)
    if not len(pos) or not len(neg):
        return float("nan")
    return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum())
                 / (len(pos) * len(neg)))


def fit_lr(X, y, l2, iters=900, lr=0.3):
    w = np.zeros(X.shape[1])
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-X @ w))
        w -= lr * (X.T @ (p - y) / len(y) + l2 * w / len(y))
    return w


def load_games(events):
    games, unit_lists = [], collections.Counter()
    for ev in events:
        con = sqlite3.connect(f"data/bcp/{ev}.sqlite"); con.row_factory = sqlite3.Row
        info = {}
        for r in con.execute("SELECT list_id,player,faction,disposition FROM lists"):
            units = collections.Counter(u[0] for u in
                                        con.execute("SELECT name FROM units WHERE list_id=?", (r["list_id"],)))
            info[r["player"]] = dict(fac=r["faction"], disp=r["disposition"], units=units)
            for u in set(units):
                unit_lists[u] += 1
        for p in json.load(open(f"data/bcp/{ev}-pairings.json")):
            if (p.get("p1_pts") is not None and p.get("p2_pts") is not None and p["p1_pts"] != p["p2_pts"]
                    and p["p1"] in info and p["p2"] in info):
                games.append((info[p["p1"]], info[p["p2"]], p["p1_pts"] > p["p2_pts"]))
    return games, unit_lists


def build(games, unit_vocab, use_units):
    facs = sorted({g[0]["fac"] for g in games} | {g[1]["fac"] for g in games})
    disps = sorted({g[0]["disp"] for g in games if g[0]["disp"]} | {g[1]["disp"] for g in games if g[1]["disp"]})
    fi = {f: i for i, f in enumerate(facs)}; di = {d: i for i, d in enumerate(disps)}
    ui = {u: i for i, u in enumerate(unit_vocab)}
    nf, nd, nu = len(facs), len(disps), (len(unit_vocab) if use_units else 0)

    def vec(a, b):
        x = np.zeros(nf + nd + nu)
        x[fi[a["fac"]]] += 1; x[fi[b["fac"]]] -= 1
        if a["disp"] in di: x[nf + di[a["disp"]]] += 1
        if b["disp"] in di: x[nf + di[b["disp"]]] -= 1
        if use_units:
            for u, c in a["units"].items():
                if u in ui: x[nf + nd + ui[u]] += c
            for u, c in b["units"].items():
                if u in ui: x[nf + nd + ui[u]] -= c
        return x

    X, Y = [], []
    for a, b, p1 in games:
        X.append(vec(a, b)); Y.append(1.0)
        X.append(vec(b, a)); Y.append(0.0)
    return np.array(X), np.array(Y), facs, disps, list(unit_vocab)


def cv(X, Y, l2, folds=5, seed=7):
    rng = np.random.default_rng(seed); ng = len(Y) // 2; order = rng.permutation(ng); a = []
    for k in range(folds):
        te = set(order[k::folds].tolist())
        tr = [i for gi in range(ng) if gi not in te for i in (2 * gi, 2 * gi + 1)]
        te_ = [i for gi in range(ng) if gi in te for i in (2 * gi, 2 * gi + 1)]
        w = fit_lr(X[tr], Y[tr], l2)
        a.append(auc((X[te_] @ w).tolist(), Y[te_].astype(bool).tolist()))
    return float(np.mean(a)), float(np.std(a))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("events", nargs="?", default="nm2026,denver-aug2026")
    ap.add_argument("--l2", type=float, default=3.0); ap.add_argument("--min-lists", type=int, default=8)
    a = ap.parse_args()
    events = a.events.split(",")
    games, unit_lists = load_games(events)
    vocab = [u for u, c in unit_lists.items() if c >= a.min_lists]
    print(f"# {len(games)} games w/ full lists ({a.events}); unit vocab {len(vocab)} (>= {a.min_lists} lists)")
    Xf, Yf, *_ = build(games, [], False)
    mf, sf = cv(Xf, Yf, a.l2)
    print(f"  faction+disposition only    : CV AUC {mf:.3f} +/- {sf:.3f}")
    Xu, Yu, facs, disps, uv = build(games, vocab, True)
    mu, su = cv(Xu, Yu, a.l2)
    print(f"  + bag-of-units (composition): CV AUC {mu:.3f} +/- {su:.3f}")
    w = fit_lr(Xu, Yu, a.l2)
    uw = w[len(facs) + len(disps):]
    order = np.argsort(uw)
    print("\nUNITS most correlated with WINNING (full-fit weights — recommendation signal):")
    for i in list(order[-8:])[::-1]:
        print(f"  +{uw[i]:.2f}  {uv[i][:34]}")
    print("UNITS most correlated with LOSING:")
    for i in order[:8]:
        print(f"  {uw[i]:.2f}  {uv[i][:34]}")


if __name__ == "__main__":
    main()
