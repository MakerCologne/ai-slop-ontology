# No-AI-Slop-Coverage — Mapping der Skill-Doku gegen den SSOT (Issue #104, Slice A)

**Status:** Slice A (DoD 1, 2, 4, 5; DoD 3 folgt in einem eigenen Slice) · **Datum:** 2026-08-29
**Abgedeckte Doku:** `skills/ai-slop-detection/references/detection-signals.md` — Abschnitte "Buzzword Detection" und "Template Phrases"
**SSOT:** `ontology.json` (ADR-0002) — Buzzword-Tiers, Phrase-Kategorien, TypePattern-Muster
**Gate:** `scripts/check_doc_signals.py` (Gate 3 in `scripts/verify.sh`); D1 = jede Doku-Phrase existiert im SSOT, D2 = jede gepinnte SSOT-Kategorie ist in der Doku mit mindestens einem Item vertreten. Selbst-Null-Check gegen strukturelle Doku-Änderungen inklusive.
**Lizenz-Schutz:** Die Rhetorik-Muster der Skill-Doku sind als Konzept aus dem "No AI slop"-Editing-Skill (petergyang/no-ai-slop, MIT) übernommen und dort bereits attribuiert. Dieses Mapping beschreibt jede Form in eigenen Worten als Konzept mit SSOT-Zuordnung; es werden keine Formulierungen der Fremdquelle reproduziert.

## Legende

- **GEDECKT** — Phrase steht im SSOT und wird von der Engine (`src/classifier.py`, Platzhalter-Mechanik #83/#88) gematcht.
- **NEU (#104)** — war in der Doku gelistet, fehlte aber im SSOT (Doku-Drift); in diesem Slice nachgezogen.
- **KORRIGIERT (#104)** — Doku-Beispiel hatte keine SSOT-Deckung; Beispiel auf ein echtes SSOT-Mitglied umgestellt.

## Mapping (Template Phrases)

| Doku-Form (eigene Beschreibung) | Status | SSOT-Ort |
|---|---|---|
| Einräumende Betonungsformel ("wichtig zu erwähnen", kontrahiert) | GEDECKT | phrases.hedging_qualifiers |
| Betonungsformel ohne Kontraktion ("es ist erwähnenswert, dass …") | **NEU (#104)** | phrases.hedging_qualifiers (`it is worth noting`, Beleg own:issue-104) |
| Abschluss-Ankündigung ("zum Schluss", "kurz gesagt") | GEDECKT | phrases.generic_transitions |
| Aufzählende Verknüpfer ("darüber hinaus", "ferner") | GEDECKT | phrases.generic_transitions |
| Rückverweis auf Gesagtes | GEDECKT | phrases.generic_transitions |
| Selbstverständlichkeits-Floskel ("braucht keine Erwähnung") | GEDECKT | phrases.hedging_qualifiers |
| Zeitgeist-Öffnung mit Einschub: "in today's [X]" | **NEU (#104)** | phrases.opening_formulas (Template, [X] = 1–4 Wörter, #83-Mechanik) — ersetzt den Varianten-Stapel, konkrete Formen bleiben matchbar |
| Aufforderung zum Mitgehen ("tauchen wir ein") | GEDECKT | buzzwords.tier1_critical und typePatterns.SEOContentFarmSlop |
| Programm-Ankündigung ("wir werden untersuchen") | GEDECKT | typePatterns.SEOContentFarmSlop |

## Mapping (Buzzword-Beispiele)

| Tier | Doku-Beispiele (nach #104) | SSOT-Ort |
|---|---|---|
| 1 (kritisch) | delve, realm, tapestry, navigating the landscape, dynamic | buzzwords.tier1_critical |
| 2 (hoch) | unleash, unlock, harness, leverage | buzzwords.tier2_high |
| 3 (moderat) | paradigm, synergy, robust | buzzwords.tier3_moderate |
| 4 (kontextabhängig) | deep dive, future-proof, quietly | buzzwords.tier4_weak |

Drei Doku-Beispiele waren vor #104 nicht über den SSOT gedeckt und wurden auf echte Mitglieder umgestellt: das Einzelwort "landscape" (SSOT kennt die Wendung "navigating the landscape"), die Bindestrich-Variante "game-changing" (SSOT: "game-changer"/"game changing") sowie die Tier-4-Zeile, deren Beispiele im SSOT Tier 2 zugeordnet sind (jetzt echte Tier-4-Mitglieder).

## Offen (Slice B)

- DoD 3 (aus #104) ist bewusst NICHT Teil dieses Slices.
- Die korpus-kalibrierten Batch-F-Listen der Skill-Skripte bleiben registrierte Abweichungen (SSOT_REGISTER/ALLOWLIST in `scripts/check_ssot.py`); ihre Doc-Spiegelung ist nicht Gate-gegenstand.
