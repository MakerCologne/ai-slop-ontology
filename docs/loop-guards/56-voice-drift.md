# Voice-Drift-Guardrail (#56)

**Status:** spec · **Verwandt:** adr/0001 (Detector, kein Rewriter — Guardrail für Loop-Rewrites), Minimum-Effective-Edit

## Voice-Budget

- max. **β = 25 % Token-Änderung** vs. Draft_0 (KL-Guardrail-Analogon, Gao et al. arXiv:2210.10760): Summe eingefügter + ersetzter Tokens / Draft_0-Tokens.
- **Non-Regression je Iteration:** Burstiness und Synonym-Vielfalt (TTR-Fenster) dürfen nicht unter den Draft_0-Wert × 0.9 fallen; Verstoß = Rollback der Iteration.

## Implementierung

`guard/voice_drift.py` (detect-only Guard, kein Score): Eingabe Draft_0 + Draft_n, Output `voice_drift: {token_change_pct, burstiness_delta, ttr_delta, verdict: ok|rollback}`. Akzeptanz: Rewrite-Serie über 5 Benchmark-Texte bleibt unter Budget; Verletzung wird reproduzierbar gemeldet.
