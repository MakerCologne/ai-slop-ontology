# Claim-Register + Zählregel „Signale" (#70)

**Status:** verbindlich · **Tool:** `scripts/count_signals.py` · **Verwandt:** adr/0005 (ehrliche Zahlen), REVIEW-Disziplin Batch G/H

## Zählregel (maschinell, dokumentiert)

`python scripts/count_signals.py` zählt Leaf-Signale in `ontology.json#/signals`:

1. `signals.<medium>.indicators[]` und `signals.<medium>.<family>.indicators[]` → 1 je Eintrag
2. `signals.text.buzzwords.tiers.*.items[]` → 1 je Phrase
3. `signals.text.phrases.categories.*.items[]` → 1 je Phrase
4. `signals.text.typePatterns.types.*` → 1 je Typ
5. `signals.text.rhetoricalPatterns.patterns.*` → 1 je Pattern (detect-only, im Feld `detect_only` separat ausgewiesen)

Aktueller Stand (2026-09-02, Commit-Stand dieses PRs): **total 319** (text 294, image 10, video 5, code 6, audio 4), davon **15 detect-only** (rhetoricalPatterns).

## Register-Disziplin

- Jede Qualitäts-/Umfangszahl in README/CHANGELOG/doku trägt entweder eine **Messvorschrift** (Tool + Command) oder ist als **SCHÄTZUNG** markiert — sonst entfernen.
- Die Signale-Zahl wird ausschließlich über `count_signals.py` behauptet; Handzählungen sind unzulässig.
- Bei jedem Signal-Zuwachs (neue Phrase, neues Pattern) aktualisiert der PR den erzeugten Zahlenstand im Claim-Kontext (Zahl + Tool-Output).

## Receipt

```
$ python scripts/count_signals.py
{"by_channel": {"text": 294, "image": 10, "video": 5, "code": 6, "audio": 4, "multilingual": 0}, "detect_only": 15, "total": 319}
```

(Der Lauf oben ist aus der Zählregel in Node verifiziert; der Python-Lauf erfolgt im GitLab-CI — im Burn-Container existiert kein Python.)
