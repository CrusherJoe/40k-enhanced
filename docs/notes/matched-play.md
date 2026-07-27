# Matched-play / event rules (11e)

Reference notes from the **Warhammer Event Companion** (v. 22 Jul 2026,
`docs/40k_event_companion.pdf`, gitignored). This is the tournament companion —
it confirms the force-disposition system and gives the scoring framework, but it
is **not** the source of per-mission scoring rules (see the gap note below).

## Mission sequence (confirms our model)

1. **Muster** a 2000-pt army, then **select one Force Disposition card** available
   to you (from your detachments' dispositions) and record it on your roster.
2. **Determine mission:** find your **opponent's** disposition symbol on **your**
   disposition card; the Primary Mission listed under it is *your* Primary Mission.
   → This is exactly our asymmetric matrix: `matrix[you][opponent]` = your mission.
3. **Determine layout:** each Primary-Mission combination has **three recommended
   terrain layouts (A/B/C)** — chosen or randomised by the organiser.
4. Battlefield is **44" × 60"**.

## VP structure (max 100 VP)

| Source | Max VP | Cap |
|---|---|---|
| Primary Mission | 45 | up to 15 VP per battle round |
| Secondary Missions | 45 | up to 15 VP/round (+ up to 20 VP per **Fixed** secondary card) |
| Battle Ready Army | 10 | painted-to-standard bonus |

- VP scored **at the end of the battle** are **not** subject to the 15/round cap.
- Most VP at battle end wins; tie = draw.

## Rules-interaction notes (designer's notes)

- **Cumulative** condition: achieving it grants VP for *both* it and the normal condition.
- **Or** conditions: you score only *one* of the or-conditions or the normal one.
- **One** (underlined): means *exactly* one, not one-or-more.
- **Leaves the battlefield:** destroyed, embarked on a Transport, or removed (e.g.
  to strategic reserves).
- **When Drawn** sections on Secondary cards apply only to *Tactical* secondaries.

## Primary-mission FAQ nuggets (hint at mission mechanics)

- **Death Trap:** scores when enemy units that started the turn in a terrain area
  are destroyed and that area is *trapped* (need not have been trapped at the moment
  of destruction).
- **Surveil the Foe:** involves *surveilling* enemy units and objectives with
  *operation markers*.
- **Vital Link:** cumulative VP for *operation markers* within *central objective(s)*
  you control.

(These reference mechanics — operation markers, "trapped" terrain, "surveilled" —
that are defined on the full mission cards.)

## GAP: where per-mission scoring lives

The actual scoring rules for each of the 25 Primary Missions (and the Secondary
Mission cards) are in the **Chapter Approved Mission Deck**, available in the
Warhammer 40,000 app — **not** in this companion. That deck is the source to pull
for the practice layer (`missions.yaml` objectives are still TODO).
