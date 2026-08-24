# 2. SSOT: ontology.json als Single Source of Truth

- **Status:** accepted
- **Datum:** 2026-08-25 (rückdokumentiert; Entscheidung fiel mit #49)

## Context and Problem Statement

Signal-Definitionen existierten doppelt: in `ontology.json` und als Inline-Python-Konstanten im Scorer. Drift zwischen beiden Darstellungen war ein aktiver Defekt (#49); Handpflege von ontology.ttl/YAML zusätzlich fehleranfällig.

## Decision Drivers

- Eine Quelle, generierte Sichten, CI-Parity (M3).
- Lexikon (#50) braucht ein verlässliches Fundament — SSOT muss vor Lexikon stehen (Sequencing, M5).

## Considered Options

### Option 1: Python-Konstanten als Quelle, JSON generiert
- Gut: für Entwickler nah am Code.
- Schlecht: Ontologie-Konsumenten (Skills, externe Tools) sehen Code als Wahrheit nicht an; Roundtrip fragil.

### Option 2: ontology.json als Quelle; Parity-Gate für Serialisierungen
- Gut: maschinenlesbar für alle Konsumenten; Parity automatisiert prüfbar.
- Schlecht: Serialisierungen (TTL/YAML) bleiben Übergangslast, bis sie generiert werden.

## Decision Outcome

**Chosen option: Option 2.** `ontology.json` ist die Quelle der Wahrheit; `scripts/check_consistency.py` erzwingt Parity gegen TTL/YAML/Scorer und läuft je Batch. Künftig werden nicht-kanonische Serialisierungen generiert statt gepflegt.

## Consequences

- **Positiv:** Drift wird CI-detektiert statt erst im Betrieb; #46 (Kollisions-Matrix) kann als Doku-Artefakt in ontology.json leben; `status`-Feld (#63) hat einen eindeutigen Ort.
- **Negativ:** Änderungen erfordern JSON-Edit + Gate-Lauf; Handserialisierungen müssen bis zur Generierung mitgezogen werden.
- **Neutral:** #50 (Lexikon) ist der erste große Consumer.

## Confirmation

- `scripts/check_consistency.py` exit 1 bei Drift (läuft je Batch, s. Burn-Log D003 Drift-Kontrolle).

## More Information

- Issues: #46, #49, #50, #54, #55
- Burn-Log-Entscheidungen (D001–D012): `research/slop-ontology-gap-2026-08-24/burn-log.md` (externe Quelle)
