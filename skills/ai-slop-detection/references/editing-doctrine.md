# Editing Doctrine — Minimum-Effective-Edit (Issue #30, Teil 1)

**Status:** redaktionelle Referenz (bearbeitbar) · **Quellen:** stop-slop
(hardikpandya, 5 Dimensionen), no-ai-slop (petergyang, 31 Checks),
humanizer (blader, Voice-Sample), brianlovin/deslop (bl-I2/I5),
humanizer-de (Evidence-Ledger, Adaptierungsbeschluss 2026-08-25).
Recherche: research/slop-ontology-gap-2026-08-24/ (deep/01–03, I17/I23;
deep/05, deslop-I5/I6; deep/06, poteto-I2) sowie
research/slop-loop-pipeline-2026-08-24/ (LOOP-I5).

Die Ontologie ist der Detektor; diese Doctrine ist der Edit-Regelsatz:
wie ein Fix aussieht, der Slop entfernt, ohne Fakten, Stimme oder
Substanz zu beschädigen. Sie ändert **keinen Scorer** — Fixes
operieren auf dem Text, die Ontology bewertet das Ergebnis.

## Kernprinzip: Minimum Effective Edit

**Der kleinste Edit, der das Signal entfernt — nicht mehr.**

Jeder zusätzliche Satz, der umgeschrieben wird, ist Gelegenheit für
neue Fehler: Faktverlust, Voice-Drift, neue Slop-Muster. Deslop ist
Chirurgie, nicht Transplantation.

- Signal-Präzedenz vor Satzherrlichkeit: Wird nur ein Wort im Satz
  getriggert, wird nur dieses Wort ersetzt („delve" → „look into"),
  nicht der Satz umgebaut.
- Ein Fix pro Fund: Jeder gemeldete Signal-Hit bekommt genau einen
  adressierten Fix. Keine „weil ich eh dabei bin"-Nebenarbeiten.
- Proportionales Cutten: Ein 400-Wort-Absatz mit einem Slop-Signal
  bekommt einen Ein-Wort- oder Ein-Satz-Fix — kein Streichbad.
  Over-Editing ist selbst ein Qualitätsfehler (siehe
  Naturalness-Guard, Issue #74/#81).

**Abbruchkriterium:** Der Edit-Loop endet, wenn (a) der Ziel-Signal-Hit
nicht mehr triggert und (b) der Re-Check (edit-self-check.md) keine
neuen durch die Bearbeitung entstandenen Signale meldet. Konvergiert
der Loop nicht in ≤ 3 Durchläufen, stoppen und den Fall als
„needs human review" markieren, statt weiter zu iterieren.

**Fertigstellungskriterium:** Ziel-Signal behoben, keine neu
eingeführten Signale, Fakten unverändert (Evidence-Gate unten),
Voice unverändert (Non-Regression unten).

## Voice-Erhalt (Non-Regression)

Die Autorenstimme ist Daten, nicht Slop. Fixes dürfen sie nicht
einebnen. Geschützte Voice-Signale (Positivprofil: human-voice.md):

- **Vokabular:** Eigene Wörter des Autors bleiben — Synonym-Rotation
  zur „Abwechslung" ist selbst ein Slop-Muster (Synonym-Rotation,
  sprachagnostisch). Ein für das Signal harmloses Lieblingswort
  bleibt stehen.
- **Kadenz:** Satzlängen-Rhythmus unangetastet. Kein Auf-/Zuschneiden
  von Sätzen, außer das Signal sitzt genau dort. Burstiness ist ein
  Merkmal menschlicher Prosa, kein Fehler.
- **Bluntness:** Schroffheit, Kürze, direkte Wertung bleiben.
  „Sanitisieren" von Ton (härtester Satz → höflichste Variante) ist
  verboten — das entfernt die Meinung, nicht das Slop.
- **Humor:** Witz, Ironie, Trockenheit bleiben. Humor-lose Glättung
  ist Over-Sanitization (Naturalness-Guard).

Non-Regression heißt: nach dem Fix müssen Vokabular-Verteilung,
Satzlängen-Verteilung und Ton am Original messbar näher sein als an
einem generischen Neutraltext. „Zu sauber" ist ein Fehlschlag.

## Evidence-Gate: Fakten sind unantastbar

**2-Fragen-Halluzinations-Guard (vor jedem Fix-Abschluss):**

1. **Did the rewrite add any fact?** Jede neue Aussage, Zahl,
   Referenz, Kausalität im Nachher-Text, die im Vorher-Text nicht
   stand, ist eine Hinzufügung → revert oder belegen.
2. **Did the rewrite remove any fact?** Jede Aussage, Zahl, Referenz,
   Kausalität im Vorher-Text, die im Nachher-Text fehlt oder
   abgeschwächt wurde („belegt" → „vermutlich", Authority-Shift),
   ist eine Entfernung → revert oder explizit als Kürzung markieren.

**Evidence-Ledger (adaptiert aus humanizer-de):** Vor dem Edit die
geschützten Anker extrahieren — Zahlen, Namen, Zitate, DOI-Links,
Autoritätsgrade („belegt/vermutlich/gefühlt"). Nach dem Edit
Vorher/Nachher gegen den Ledger prüfen: anchor_diff (Anker fehlt oder
ist verändert) und authority_shift (Autoritätsgrad gedrückt) sind
BLOCK-Kriterien — der Edit wird verworfen, unabhängig vom Slop-Score.

**Invariante:** Deslop löscht keine Facts. Ein Text, der nach dem Fix
besser scored aber ärmer an Information ist, ist ein schlechter Fix.

## Verhältnis zu Skill und Checks

- Diese Doctrine definiert **Regeln des Edits** (was ein Fix darf).
- `references/edit-self-check.md` (Issue #30, Teil 2) definiert den
  **Prüfprozess** (~20 Checks, What-changed-Output, Re-Check-Loop
  als Skill-Schritt 4b).
- Report-Regeln (Agenten-Output 1–3 Sätze, zweistufiges Cleanup
  deslop → simplify) sind Skill-Verhalten (Issue #30, Teil 3).
- Voice-Zielzustand: `references/human-voice.md` (#21).
- Anchor-Drift-Detektion (detect-only): Issue „Anchor-Drift-Signal"
  liefert den Detektor für das Evidence-Gate.

## depends-on

- #21 (human-voice.md) — Voice-Referenz, existiert.
- Anchor-Drift-Signal — detect-only-Kern für Evidence-Gate,
  separates Issue (in Arbeit).
