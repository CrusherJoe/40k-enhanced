# Death v2 — Iron Hands Pivot Assessment

Evaluation of an **Iron Hands** pivot for the Death v2 project, built on Jared Garcia's
"Baby Shark" list (6th at Northern Maelstrom 2026) and tested two ways: against the *real*
opponents Garcia beat on the day, and — as an out-of-sample stress test — against the top of a
completely different event (Denver 40K Fight Club Aug Open '26). Data from the committed field
pulls (`data/bcp/nm2026*`, `data/bcp/denver-aug2026*`); sim via the positional board-control
runbook.

## Headline

- **Baby Shark validates as the Death v2 chassis.** It went **5-1 in its own NM2026 meta** and,
  in a cross-event sim against a field it never saw, was **board-favoured in 8 of 9** Denver top
  finishers. The board-control identity is meta-portable, not matchup-fit to one event.
- **The engine is durability, not alpha.** The T6 Heavy Intercessors anchor the objective war in
  every game (82-97% survival); the list wins by out-lasting, not out-punching.
- **The ceiling is set by two identifiable shapes**, not by a faction: elite Dark Angels
  burst/secondary lists, and mass-OC durable gunlines. Both are prep-able.
- **Recommendation: pivot to Iron Hands.** This is a tougher, more forgiving board-control
  chassis than a Lancer-less Knights rebuild, and it does the thing the LSO data said Knights
  should do (durable board hold + concentrated guns) more naturally than Knights can.

## 1. The list — "Baby Shark" (Iron Hands, Librarius Conclave, 1990pts)

| Unit | Pts | Role |
|---|--:|---|
| Terminator Assault Squad (10, 2+/4++, thunder hammers) | 360 | Hammer / board anchor |
| Hellblaster Squad | 220 | Ranged workhorse |
| Heavy Intercessor Squad (T6) | 200 | **Durable board anchor** |
| Gladiator Lancer | 160 | Anti-tank |
| Assault Intercessor Squad | 150 | Board / trade |
| Ballistus Dreadnought | 150 | Anti-tank / fire support |
| Infiltrator Squad | 110 | Screen / deny deep strike |
| Librarian ×2 | 85 / 95 | Conclave enablers |
| Caanok Var | 90 | Character |
| Iron Father Feirros | 85 | Iron Hands buff character |
| Ancient in Terminator Armour | 85 | Terminator support |
| Apothecary Biologis | 80 | Buff / heal |
| Intercessor Squad | 80 | Board / OC |
| Apothecary | 40 | Heal |

Loads into the sim with **zero unresolved datasheets** — fully modellable.

## 2. NM2026 — the actual gauntlet to 6th (5-1)

What Garcia beat on the day, with the sim's read of each matchup:

| R | Opponent (finish) | Actual | Sim verdict | Board margin |
|--:|---|:--:|---|--:|
| 1 | Rothman — Space Marines (#13) | W 90-75 | HARD | −0.62 |
| 2 | Ganshyn — Grey Knights (#93) | W 85-71 | FAVOURED | +0.69 |
| 3 | Pedretti — Death Guard (#86) | W 100-79 | EVEN / GRINDY | +0.14 |
| 4 | Cook — Space Wolves (#21) | W 73-43 | FAVOURED | +1.04 |
| 5 | **McCord — Dark Angels (#2)** | **L 79-99** | FAVOURED | +1.27 |
| 6 | Howard — Chaos Knights (#16) | W 97-22 | FAVOURED | +0.95 |

This is a genuine 5-1 — three top-25 opponents beaten, and the only loss to the eventual event
runner-up. The board model rated the McCord game **favourable** (+1.27) yet Garcia lost 79-99: the
loss came from what the positional sim does not capture — top-tier Dark Angels burst + secondary
scoring, the same apex archetype flagged UNFAVOURABLE at LSO.

## 3. Denver cross-event stress test (out-of-sample)

Baby Shark run against the loadable Denver top finishers — a field it never faced, in a different
meta (Orks/Daemons/Guard-heavy, no DA/Votann apex). 500 games/matchup.

| Plc | Opponent | Faction | Sim verdict | Board margin |
|--:|---|---|---|--:|
| 1 | Mason Mutz | Orks (winner) | FAVOURED | +1.60 |
| 2 | John Gianforte | Chaos Daemons | FAVOURED | +0.43 |
| 5 | Steven Pampreen | Orks | FAVOURED | +0.85 |
| 6 | Joel Davis | Orks | FAVOURED | +1.42 |
| 7 | Calvin Fertig | Astra Militarum | FAVOURED | +0.44 |
| 8 | Hunter Williams | Dark Angels | FAVOURED | +0.84 |
| 9 | Lane Nusbaum | Astra Militarum | **EVEN / GRINDY** | −0.27 |
| 10 | Khael Hopkins | Necrons | FAVOURED | +0.44 |
| 11 | Colin Kay | SM — Librarius Conclave | FAVOURED | +0.90 |

**Favoured 8 · Even 1 · Hard 0.** The board margin is Garcia minus opponent (avg objectives/turn).

Three findings:

1. **The chassis travels.** Board-favoured in 8 of 9 against a meta it never saw. The durable T6
   Heavy Intercessors are the MVP anchor in every matchup — they win the objective war regardless
   of opponent.
2. **Dark Angels is not automatically the wall.** Denver's #8 DA came back FAVOURED (+0.84),
   whereas NM2026's McCord DA *beat* Garcia. It is not "DA hard" — it is "elite DA burst/secondary
   lists" that exceed the board model. Ordinary DA, Baby Shark out-grinds.
3. **Beats a standard Marine mirror.** vs #11 Colin Kay's Librarius Conclave Marines (+0.90): the
   Terminators (49.6 wounds/turn) plus the T6 wall push Kay off the board entirely by R4. Against
   the "normal" Marine list, Baby Shark is simply more durable and more board-sticky.

## 4. The two threats — and how they differ

Across both events, the games that trouble Baby Shark cluster into **two shapes** that want
opposite answers:

- **Elite burst + secondary game** (McCord DA, NM2026). The board reads favourable but they win on
  removal speed and secondary tempo. *Answer:* faster threat removal / secondary denial; do not
  trust the board lead alone.
- **Mass-OC durable gunline** (Nusbaum "Grizzled Company" Guard, Denver). They out-board Baby Shark
  early (objectives 1.5/2.1/1.6 vs 1.0/0.6/0.9 across R1-3) by flooding OC bodies, anchoring on a
  Rogal Dorn Commander, and fielding Ogryns + a Hellhound the list **can't reliably remove**.
  *Answer:* more early board presence and a plan for un-removable durable chaff.

## 5. Consistent liabilities (screen these every game)

The fragile enablers die for nothing if exposed and appear as liabilities across matchups:
**both Librarians, the Ancient in Terminator Armour, the Apothecary Biologis, and the Ballistus
Dreadnought.** Screen or hold them until they matter; the Conclave engine is also the soft spot.

## 6. Recommendation

**Pivot to Iron Hands / Baby Shark as the Death v2 base.** It is validated across two metas as a
durable, meta-portable board-control list, and its identity aligns with the empirical LSO finding
(durable board hold + concentrated guns beats the melee-investment Knights build). Its ceiling is
set by two specific, identifiable archetypes — both of which we now know to prep for.

*Next steps if adopted: (a) test a list tweak that shores up the mass-OC-gunline matchup without
losing the durable core; (b) build a secondary-denial plan for elite DA; (c) re-run both gauntlets
after any list change to confirm the board identity holds.*
