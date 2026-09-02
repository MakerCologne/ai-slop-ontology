# 8. Geltungsbereich: Human/Ideological Slop

- **Status:** proposed (decision-needed — Abschluss nur nach Freigabe, Issue #90)
- **Datum:** 2026-09-02
- **Issues:** #90 (dieses ADR), #91 (bewerteter Vorschlag A vs. B), Epic #89, verwandt #86, #92, #93, #94–#98

## Context and Problem Statement

Die Human-Slop-Recherche (2026-08-28, Epic #89) zeigt: Willisons drei Bedingungen und Kommers' Prototypen beschreiben auch menschlich verfassten Output, sobald Sorgfalt/Verifikation fehlen und Distribution Push ist. Die Ontologie kennt bereits `PoliticalSlop` / `DisinformationSlop` (Intent) und `Democracy Risk` (Harm), aber keine Schwesterklasse `HumanSlop` und keinen Detektor für ideologische Ritualprosa.

Ohne Entscheidung entstehen zwei Fehlpfade:

1. Ein Score-Gate auf politische Sprache macht den Detector zum Zensor (Verstoß gegen adr/0001).
2. Das Phänomen bleibt unsichtbar — `PoliticalSlop` und `Democracy Risk` bleiben tote Klassen.

## Decision Drivers

- adr/0001: Detector, kein Rewriter — erst recht kein Gesinnungsscanner.
- adr/0006: neue Module default detect-only.
- adr/0005: Korpus-Disziplin — Hard-Negatives sind Pflicht, kein Benchmark-Gaming.
- SIGNAL-DoD: 3/3/2 Fixtures je Pattern, keine Auto-Rewrite-Disziplin.
- #86: `HumanAuthoredWorkSlop` (Work/SEO-Slop) stellt dieselbe Geltungsfrage für Arbeitstexte.

## Considered Options

### Option A — In-scope mit eigenem Score (`HumanSlop` + `polemic_risk`)
- Gut: Phänomen wird messbar; RAG-Routing und Harm-Graph anschließbar.
- Schlecht: verführt zum Score-Gate auf politische Sprache; Noisy-OR würde Political Copy mit SEO-Slop verrechnen; hohes FP-/Missbrauchsrisiko ohne ausgereiftes Hard-Negative-Korpus.

### Option B — In-scope, detect-only (Klasse/Lexikon + Rhetorik-Layer, keine Zahl)
- Gut: kleinster Schritt, der das Phänomen messbar macht, ohne den Detector zum Gesinnungsscanner zu machen; passt zum bestehenden Vertrag (`named evidence`, `keep_when`, `slop rhetoric`); leicht reversibel; Anschluss an #76/#73/#77 DE-Layer.
- Schlecht: bleibt Oberflächenmuster — kein RAG-Routing, kein Harm-Graph; Forschungsbegriffe (Ethnopluralismus, Brandmauer) werden keine Klassen.

### Option C — Out-of-scope (Forschungsnotiz in `REFERENCES.md`)
- Gut: null FP-Risiko, null Aufwand im Scorer.
- Schlecht: verwirft kanonischen Bestand (`PoliticalSlop`, Harm-Typ Democracy Risk); #86 kann Work/SEO-Slop zwar abdecken, nicht Ideologie/Polemik/Panik.

## Bewertung A vs. B (Detail in #91)

| Kriterium | A Ontologie | B Rhetorik |
|---|---|---|
| Passung adr/0001 + 0006 | Mittel (Score-Verführung) | **Hoch** |
| Agent-Nutzen kurzfristig | Klassennamen ohne Matcher | **`slop rhetoric` liefert Evidence** |
| Agent-Nutzen mittelfristig | **RAG-Routing, Harm-Graph** | „Muster erkannt" |
| FP-/Missbrauchsrisiko | Hoch (wenn Score) | **Mittel (keep_when + Hard-Negatives)** |
| Forschungs-Treue | **Hoch** | Mittel |
| Aufwand | M–L | **S–M** |
| Reversibilität | Schwer | **Leicht** |

## Recommendation

**B als Default, A als anschließende Erweiterung nach explizitem Opt-in** (`--genre ideology`, analog adr/0004 genre-opt-in). C wird verworfen.

Konsequenzen:

- `polemic_risk` existiert nicht, bevor das Korpus aus #98 steht (Precision ≥ 0.95 auf Hard-Negatives).
- RAG-Gate-Auswirkung nur bei der Kombination `polemic_risk` + Harm `Democracy Risk` + Entmenschlichung → `CriticalReviewRequired` — und auch das zunächst nur als named evidence, nicht als Score.
- Abgrenzung „Policy-Argument vs. Ritual-Frame" (10 Zeilen): Ein Policy-Argument nennt Akteur, Instrument, Beleg und ist falsifizierbar (Zahlen mit Nenner, Zeitraum, Quelle; Verfahren; Rechtsfall). Ein Ritual-Frame reproduziert einen Slogan ohne Information-Gewinn: Totalerklärungen („Systemparteien"), Herkunft als Kollektivschuld, Erlöser-Schemata, unfalsifizierbare Deutungsschablonen, Entmenschlichung. Slop beginnt nicht an der Position, sondern an Template, Unfalsifizierbarkeit und fehlendem Informationsgewinn — die bewertete Haltung bleibt beim Leser.
- Für #86: gleicher Grundsatz — Slop ist ein Risikoprofil (Template, fehlende Sorgfalt, Push-Distribution), keine Autorschaftsklasse.

## Consequences

- **Positiv:** Detector bleibt Zensor-frei; Phänomen wird benennbar und evolutionär promotbar (Lebenszyklus #63).
- **Negativ:** Ideologische Ritualprosa bleibt zunächst unscored — bewusste, dokumentierte Lücke.
- **Neutral:** Option A wird nicht verworfen, sondern an Opt-in + Korpus-Reife (#98) gebunden.

## More Information

- Epic #89; Umsetzung B: #92 (Rhetorik-Layer), #95–#97 (Fallstudien), #98 (Eval-Korpus).
- Umsetzung A (nach Freigabe): #93 (Ontologie-Extension), #94 (Ethnopluralismus-Lexikon).
- Kalibrierungs-Ehrlichkeit: #106/#107.
