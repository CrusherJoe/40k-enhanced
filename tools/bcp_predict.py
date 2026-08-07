#!/usr/bin/env python3
"""bcp_predict.py — a DATA-DRIVEN win-probability model learned from real BCP games.

Complements the mechanistic sim (which we keep — it becomes a feature source). Learns P(p1 wins) from real
outcomes in data/bcp/corpus/games.json (built by tools/bcp_corpus.py). Features are ANTISYMMETRIC — each
game is added both ways (p1 vs p2 and swapped, label flipped) so the model can't cheat on player order and
learns per-faction / per-disposition edges directly. Reports cross-validated AUC (the honest predictiveness
number) vs the sim's real-game AUC of ~0.47, plus empirical matchup-lookup baselines.

  python3 tools/bcp_predict.py [--folds 5] [--l2 2.0]
"""
import json, argparse
import numpy as np


def load():
    d = json.load(open("data/bcp/corpus/games.json"))
    return d["games"]


def auc(scores, labels):
    pos = np.array([s for s, l in zip(scores, labels) if l], float)
    neg = np.array([s for s, l in zip(scores, labels) if not l], float)
    if not len(pos) or not len(neg):
        return float("nan")
    return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum())
                 / (len(pos) * len(neg)))


def fit_lr(X, y, l2=2.0, iters=800, lr=0.3):
    w = np.zeros(X.shape[1])
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-X @ w))
        w -= lr * (X.T @ (p - y) / len(y) + l2 * w / len(y))
    return w


def featurize(games):
    facs = sorted({g["p1_fac"] for g in games} | {g["p2_fac"] for g in games})
    disps = sorted({g["p1_disp"] for g in games if g["p1_disp"]} |
                   {g["p2_disp"] for g in games if g["p2_disp"]})
    fi = {f: i for i, f in enumerate(facs)}; di = {d: i for i, d in enumerate(disps)}
    nf, nd = len(facs), len(disps)

    def vec(f1, d1, f2, d2):
        x = np.zeros(nf + nd)
        x[fi[f1]] += 1; x[fi[f2]] -= 1                 # antisymmetric faction edge
        if d1 in di:
            x[nf + di[d1]] += 1
        if d2 in di:
            x[nf + di[d2]] -= 1
        return x

    X, Y = [], []
    for g in games:
        X.append(vec(g["p1_fac"], g["p1_disp"], g["p2_fac"], g["p2_disp"])); Y.append(1.0)
        X.append(vec(g["p2_fac"], g["p2_disp"], g["p1_fac"], g["p1_disp"])); Y.append(0.0)  # swapped
    return np.array(X), np.array(Y), facs


def cv_auc(X, Y, folds, l2, seed=7):
    rng = np.random.default_rng(seed)
    # fold by original game (rows come in swapped PAIRS): keep a pair in the same fold
    ng = len(Y) // 2
    order = rng.permutation(ng)
    aucs = []
    for k in range(folds):
        te = set(order[k::folds].tolist())
        tr_rows = [i for gi in range(ng) if gi not in te for i in (2 * gi, 2 * gi + 1)]
        te_rows = [i for gi in range(ng) if gi in te for i in (2 * gi, 2 * gi + 1)]
        w = fit_lr(X[tr_rows], Y[tr_rows], l2=l2)
        s = X[te_rows] @ w
        aucs.append(auc(s.tolist(), Y[te_rows].astype(bool).tolist()))
    return float(np.mean(aucs)), float(np.std(aucs))


def lookup_auc(games, key, seed=7):
    """Empirical antisymmetric matchup win-rate lookup (leave-one-out-ish via CV) for a keying function."""
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(games))
    folds = 5
    scores, labels = [], []
    for k in range(folds):
        te = set(idx[k::folds].tolist())
        wr = {}  # key -> [wins, n] from the TRAIN split
        for i, g in enumerate(games):
            if i in te:
                continue
            a, b = key(g["p1_fac"], g["p1_disp"]), key(g["p2_fac"], g["p2_disp"])
            wr.setdefault((a, b), [0, 0]); wr[(a, b)][0] += g["p1_won"]; wr[(a, b)][1] += 1
            wr.setdefault((b, a), [0, 0]); wr[(b, a)][0] += (not g["p1_won"]); wr[(b, a)][1] += 1
        for i in te:
            g = games[i]
            a, b = key(g["p1_fac"], g["p1_disp"]), key(g["p2_fac"], g["p2_disp"])
            wn, n = wr.get((a, b), [0, 0])
            scores.append((wn + 0.5) / (n + 1))          # Laplace-smoothed win rate
            labels.append(bool(g["p1_won"]))
    return auc(scores, labels)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folds", type=int, default=5); ap.add_argument("--l2", type=float, default=2.0)
    a = ap.parse_args()
    games = load()
    print(f"# {len(games)} real decided games in the corpus")
    X, Y, facs = featurize(games)
    m, s = cv_auc(X, Y, a.folds, a.l2)
    print(f"\nLEARNED MODEL (logistic, faction+disposition, {a.folds}-fold CV):")
    print(f"  cross-validated AUC = {m:.3f} +/- {s:.3f}   (sim's real-game AUC ~0.47; 0.5 = no signal)")
    print("\nEMPIRICAL LOOKUP BASELINES (5-fold):")
    print(f"  faction x faction            AUC = {lookup_auc(games, lambda f, d: f):.3f}")
    print(f"  disposition x disposition    AUC = {lookup_auc(games, lambda f, d: d):.3f}")
    print(f"  (faction,disp) x (faction,disp) AUC = {lookup_auc(games, lambda f, d: (f, d)):.3f}")
    # learned per-faction strengths (full-data fit) — interpretable sanity check
    w = fit_lr(X, Y, l2=a.l2)
    order = np.argsort(w[:len(facs)])
    print("\nLEARNED FACTION EDGE (full fit; + = wins more, all else equal):")
    for i in list(order[:5]) + list(order[-5:]):
        print(f"  {facs[i][:26]:26} {w[i]:+.2f}")


if __name__ == "__main__":
    main()
