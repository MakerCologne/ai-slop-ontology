# Learn-Input-Standard (Issue #120)

**Status:** implementiert · **Aufwand:** S · **Prio:** P2 · **Verwandt:** #29 (Learning-Store), #11 (slop.json)

## Problem

Der Learning-Store (#29) definierte keinen Input-Standard. Landscape-Befunde
(sloppoke, flamehaven01, axonscanner) zeigen: Der Input muss **simpel** sein —
kein UI, kein Schema-Zwang — sonst wird das Lernen gar nicht benutzt.

## Standard (messbar)

**Ein Freitext-Bezug + optionaler Datei-/Pfad reicht:**

```bash
# minimal — nur Freitext
python skills/ai-slop-detection/scripts/slop_scorer.py \
  --learn "false positive on src/foo.rs, buzzwords ok hier"

# mit Datei = exakte Sample-Exemption (wie --mark-not-slop, aber ohne Schema-Zwang)
python skills/ai-slop-detection/scripts/slop_scorer.py \
  --learn "genre copy, ok" --file text.md --signal buzzwords --by hertha

# alternativ direkt am Store-Modul
python skills/ai-slop-detection/scripts/learning_store.py \
  learn "false positive on src/foo.rs" --file src/foo.rs
```

## Regeln

1. `note` (Freitext) ist Pflicht und nie leer; alles andere ist optional.
2. `--signal` optional; Default `reviewed` (kann später verfeinert werden —
   der Eintrag ist append-only, Refinement = neuer Eintrag).
3. `--file` optional:
   - mit `--file`: Sample-Hash der Datei → echte Exemption beim Re-Run.
   - ohne `--file`: Sample-Hash des Freitexts selbst → Kontext bleibt
     attribuierbar, aber keine Score-Wirkung.
4. `--store` optional; Default `not_slop.jsonl` neben der Datei bzw. im cwd.
5. Keine Validierung über Existenz hinaus; bewusst „under-strict", damit
   der schnellste Weg der niedrigschwellige ist (axonscanner:
   self-learning backlog; sloppoke: `slop learn "…"` One-Liner).

## API

`learning_store.learn_entry(path, note, signal_id=None, sample_text=None, added_by="manual")`

## Akzeptanz (getestet)

- `--learn "text"` ohne weitere Flags legt einen Eintrag an (returncode 0).
- Mit `--file` wird beim Re-Run die Signal-Familie als `exempted` gemeldet.
- Leerer/fehlender Freitext → Fehler (exit 2).
- Schema des Eintrags unverändert zu #29: `{signal_id, sample_hash, note, date, added_by}`.

## Quellen

- https://github.com/peeramid-labs/sloppoke
- https://github.com/flamehaven01/AI-SLOP-Detector
- https://github.com/AI-Labs-Pvt-Ltd-Nepal/axonscanner
- research/slop-detection-landscape-2026-09-02/ (landscape.md)
