# Voice-Drift-Guardrail (#56)

**Status:** implemented (src/voice_drift.py · tests/test_voice_drift.py · Loop-Integration in src/deslop_loop.py) · **Verwandt:** adr/0001 (Detector, kein Rewriter — Guardrail für Loop-Rewrites), Minimum-Effective-Edit

## Voice-Budget

- max. **β = 25 % Token-Änderung** vs. Draft_0 (KL-Guardrail-Analogon, Gao et al. arXiv:2210.10760): Summe eingefügter + ersetzter Tokens / Draft_0-Tokens.
- **Non-Regression je Iteration:** Burstiness und Synonym-Vielfalt (TTR-Fenster) dürfen nicht unter den Draft_0-Wert × 0.9 fallen; Verstoß = Rollback der Iteration.

## Implementierung

`src/voice_drift.py` (detect-only Guard, kein Score; `guard/voice_drift.py`-Pfad aus der Spec auf src/ gemappt): `evaluate(draft_0, draft_n)` → `VoiceDriftVerdict {verdict: ok|budget|regression|too_short, token_change_pct, burstiness_0/n/delta, ttr_0/n/delta, reasons}`.

- **token_change_vs:** (removed + inserted) / draft_0-Tokens, gedeckelt bei 1.0 — exakt die Spec-Formel (Summe eingefügter + ersetzter Tokens / Draft_0-Tokens), nicht die symmetrische Loop-Interne-Heuristik.
- **burstiness:** Variationskoeffizient der Satz-Längen (Sqrt(Var)/Mean); gleichförmiger Maschinenrhythmus kollabiert → 0.
- **lexical_diversity:** windowed TTR (Fenster 50) über Content-Words (leichter Stopword-Filter, DE+EN) als Synonym-Vielfalt-Proxy, längenrobust.
- **Non-Regression:** Floor = draft_0 × 0.9 je Metrik; Verstoß → `regression`.
- **Loop-Integration (#56 → #51):** DeslopLoop prüft zusätzlich zum bisherigen per-Step-voice_budget jetzt kumulativ vs Draft_0; Ablehnung → `rejected_voice_drift_{budget|regression}` mit vollständigem `voice_drift`-Payload im Iterations-Audit (#61-Format).

Akzeptanz erfüllt: Verletzung wird reproduzierbar gemeldet (11 Tests, inkl. Loop-Roundtrips mit Fake-Detektor); Rewrite-Serien unter Budget laufen unverändert durch. Verbleibend (out of scope, S-Aufwand): Benchmark-Texte-Serie aus eval/ als End-to-End-Akzeptanz.
