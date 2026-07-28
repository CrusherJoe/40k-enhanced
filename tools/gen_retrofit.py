# -*- coding: utf-8 -*-
"""gen_retrofit.py — regenerate GV / BT-'send help' / BT-Bastion on the NEW STANDARD: real-mission
sim (sim_game.results_legacy, 10k games) + generic deliverables (gen_list -> Excel Analysis + PDF
Runbook). Retires the old abstract-score docs. Run: PYTHONPATH=tools:src python3 tools/gen_retrofit.py
"""
import sim_game, gen_list
import gv_data, bt_data, bt_bastion_data
import mc_gv_sim, mc_bt_sim, mc_bt_bastion_sim

# (data module, ARCH, my disposition, list profile, cust_sec, analysis key, runbook key, colour, finding)
LISTS = [
    (gv_data, mc_gv_sim.ARCH, "purge-the-foe",
     dict(kill=.72, action=.62, ctrl=2.2, home=.15, opp_ctrl=2.0, opp_frag=.0), 0.95,
     "gv-analysis", "gv-runbook", "6b8e23",
     "'Great Value' is a durable Purge gunline: it FEASTS on Priority-Assets armies (Destroyer's Wrath "
     "kill-mission) and out-lasts most, but the true horde out-bodies it (the one hole)."),
    (bt_data, mc_bt_sim.ARCH, "take-and-hold",
     dict(kill=.68, action=.60, ctrl=2.1, home=.18, opp_ctrl=2.0, opp_frag=.08), 0.92,
     "bt-analysis", "bt-runbook", "202028",
     "The FIXED 'send help' list is a deliberately-hard Take-and-Hold brief: an underdog that lives on "
     "delivery landing + holding, and folds when the alpha is denied."),
    (bt_bastion_data, mc_bt_bastion_sim.ARCH, "take-and-hold",
     dict(kill=.64, action=.64, ctrl=2.4, home=.12, opp_ctrl=1.9, opp_frag=.04), 0.95,
     "bt-bastion-analysis", "bt-bastion-runbook", "202028",
     "The Bastion Task Force is a durable hold-and-debuff army: it grinds Take-and-Hold matchups on "
     "quality + the auspex-scan control toolkit; the horde remains the hardest game."),
]


def main():
    for D, arch, disp, prof, sec, ak, rk, colour, finding in LISTS:
        # ARCH is built in D.MATCHUPS order (verified parallel), so rows align by index.
        assert len(arch) == len(D.MATCHUPS), f"{ak}: ARCH {len(arch)} != MATCHUPS {len(D.MATCHUPS)}"
        rows = sim_game.results_legacy(arch, disp, prof, games=10000, cust_sec=sec)
        a, b, w = gen_list.build(D, rows, ak, rk, disp, finding, colour)
        print(f"{ak:22} weighted ~{w}%  ->  {a.split('/')[-1]}  |  {b.split('/')[-1]}")


if __name__ == "__main__":
    main()
