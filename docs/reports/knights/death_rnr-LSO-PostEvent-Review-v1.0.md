# death_rnr — LSO 2026 Post-Event Review
**Version 1.0 · 2026-08-06** · Imperial Knights, "This List Tastes Like Death by Rock and Roll"

Post-mortem of the Lone Star Open 2026 (328 players, 6 rounds), built from the real BCP results
(`data/bcp/lso2026-placings.json`, `-pairings.json`) cross-referenced against our pre-event
archetype verdicts and the death_rnr field dossier.

## Headline

- **Event winner:** Junior Aflleje — Leagues of Votann (Priority Assets).
- **Joe / death_rnr:** **2-4, 244/328** (Imperial Knights, Valourstrike Lance, Purge the Foe).
- **Two other Knights top-6:** Jason Weeks **4th (6-0)**, Nathaniel Bjorge **6th (5-1)** — the list
  archetype top-cuts; death_rnr's run underperformed the field's Knights.

## 1. Did our verdicts hold up?

Our verdicts rate **how death_rnr fares vs an archetype** (not the archetype's raw strength). Tested
against actual finishes, the archetypes we flagged **UNFAVOURABLE** (hardest for Knights) were the
genuine top of the field:

| Archetype | Our read | Actual avg finish | Best |
|---|---|--:|--:|
| Dark Angels — Company of Hunters | UNFAVOURABLE | **80** | 2nd |
| T'au — Experimental Prototype | UNFAVOURABLE | **93** | 10th |
| Necrons — Cursed Legion | UNFAVOURABLE | 118 | 23rd |
| Votann — Needgaård | COIN-FLIP | 126 | **1st** |
| Custodes — Shield Host | FAVOURABLE | 170 | 109th |

Threat-assessment was **directionally correct** — the invuln-negation / Dev-wound / out-OC lists we
called hardest finished highest; the FAVOURABLE pick (Custodes) was a weak meta choice.
**Caveat:** verdict *tier* is not a power ranking — e.g. Necrons Awakened Dynasty (C'tan wall) is
HARD *for us* yet finished low overall (avg 197). Use verdicts as matchup guidance, not tiering.

### Joe's 6 games vs our reads
| R | Res | Score | Opponent archetype | Our read |
|---|---|---|---|---|
| 1 | L | 72-73 | DA — Wrath of the Rock | HARD → lost by **1** |
| 2 | W | 89-61 | Necrons — Hand of the Dynasty (C'tan) | HARD → **won** (play-the-mission worked) |
| 3 | W | 97-86 | Chaos Space Marines | — |
| 4 | L | 82-92 | DA — Librarius Conclave | COIN-FLIP → close L |
| 5 | L | **33-98** | Imperial Knights (mirror) | MIRROR → blown out |
| 6 | L | 73-84 | Grey Knights — Banishers | COIN-FLIP → close L |

Reads were sound: the two HARD games were a 1-point loss and a win; four of six were within ~11.
The killer was the **mirror blowout (33-98)**, which also tanked tiebreakers.

## 2. The whole Knights field (18 players) — what wins

| Plc | Rec | Player | Disposition | Detachment | Build | Lancer |
|--:|---|---|---|---|---|:--:|
| 4 | 6-0 | Jason Weeks | Take and Hold | Gate Warden Lance | 4 Kn + 3 Armiger + Sisters/Immolator | no |
| 6 | 5-1 | Nathaniel Bjorge | Priority Assets | Valourstrike | 5 gun-Knights (pure) | no |
| 31 | 5-1 | Lewis Hersman | Purge the Foe | Valourstrike | 4 Kn + 2 Armiger | no |
| 40 | 4-2 | Dick McTrickle | Purge the Foe | Valourstrike | 3 Kn + 5 Armiger | no |
| 68 | 4-2 | Gator Murray | Purge the Foe | Valourstrike | 4 Kn + Lancer + allies | **yes** |
| 138 | 3-3 | Chad Stubblefield | Purge the Foe | Valourstrike | 5 Kn (pure) | no |
| … | | (mid-pack) | | | | mixed |
| 244 | 2-4 | **Joe Beddoe** | Purge the Foe | Valourstrike | 3 Kn + Lancer + Warglaive + Navigator | **yes** |
| 281 | 1-4 | Lacey Huff | Reconnaissance | Dominus Foebreakers | 2 Kn + 8 Armiger | no |
| 298 | 1-4 | Alex Hernandez | Purge the Foe | Valourstrike | 5 Kn + Lancer | **yes** |
| 317 | 0-3 | Corbin King | Purge the Foe | Valourstrike | 2 Kn + 8 Armiger | no |

**The signal, ranked by strength:**
1. **Cerastus Lancer = the clearest negative.** No-Lancer avg **134** vs Lancer avg **225** (n=10 vs 8);
   all top-4 Knights ran no Lancer; best Lancer finish was 68th. The ~415-pt melee investment is the
   "Castellan's worth of shooting" our firepower-as-denial law warned against — the field confirms it.
   *(Correlation, n=18 — not proof, but consistent and doctrine-aligned.)*
2. **Disposition = secondary.** Objective disps (166) only mildly beat Purge (181); Purge/no-Lancer
   players still placed 31st & 40th. Purge wasn't the problem — the Lancer + build were.
3. **Two proven winning shapes, both Lancer-less, max firepower/board:** all-gun 5-Questoris
   (Bjorge) OR guns + cheap OC bodies (Weeks: Armigers + Sisters/Immolator). Allies help but aren't
   required.
4. **death_rnr combined the worst-correlated traits** — the Lancer + a thin board (only a Warglaive
   + Navigator for OC) — on the kill-primary disposition.

## 3. Recommendations for the next event

- **Drop the Cerastus Lancer.** Reinvest into either a 5th gun-Knight (Bjorge model) or Armigers +
  a cheap OC/action ally package (Weeks model). This is the single highest-leverage change.
- **Add real board/OC presence** if going the Weeks route (Armigers + a Sisters squad + Immolator) —
  it directly fixes the "always outnumbered, lose the primary" problem.
- **Disposition is a lighter lever** — Take and Hold / Priority Assets edged Purge, but a good
  no-Lancer Purge list still top-30s. Decide disposition by the build, not the reverse.
- **Mirror prep matters** — a Knights mirror decided by first turn + Rotate discipline swung Joe's
  event (33-98). The all-gun build wins the mirror (Bjorge 100-69); the Lancer build lost it.

*The pre-event verdicts + field dossier were sound as matchup intel; the list-construction was the
gap. Both winning Knights builds point the same way: more guns/board, no Lancer.*
