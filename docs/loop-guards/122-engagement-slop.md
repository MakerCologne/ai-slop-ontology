# Engagement-Slop-Signale: Approval Theater + Counterfactual (#122)

**Status:** spec (Signal-Kandidaten, detect-only) · **Quelle:** bhanvinayer/PRISM · **Verwandt:** #58 (≥2 Nachweise), SIGNAL-DoD

## Signale

1. **Approval Theater:** generische Review-/Approval-Kommentare — Kosinus-Ähnlichkeit gegen generische Phrase-DB; passt der Kommentar auf jeden beliebigen Diff, ist er kein Review.
2. **Counterfactual-Test:** „Würde derselbe Kommentar auf unrelated PRs passen?" — übertragbar auf Buzzword-Sätze: „passt dieser Satz auf jedes Projekt?"
3. **Circular Explanation:** tautologische Definition im Satz („The auth module validates authentic user authentication") — Prosa-Signal, direkt in die Ontology (`signals.text`-Familie) übernehmbar.

## DoD vor Promotion

Eigenes Signal-Issue je Signal mit 3/3/2-Fixtures (SIGNAL-DoD), Hard-Negatives: substantive Reviews mit Fachjargon; detect-only bis FP=0 auf Hard-Negatives (adr/0006). Review-Slop jenseits der AI-Origin-Frage ist damit abgedeckt.
