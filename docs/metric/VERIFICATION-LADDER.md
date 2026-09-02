# Metrik-Design: Verification Ladder für „fake-done" (Code-Achse) (#121)

**Status:** spec (nicht aktiviert) · **Verwandt:** #55 (Hard-Gates), adr/0006 (detect-only), Quelle: AI-Labs/axonscanner

## Problem

Für die Code-Achse fehlt eine Gesamtmetrik, die „Finish-ness" vom Stil trennt. Stil-Signale (#9) sagen nichts darüber, ob behauptete Funktion real existiert.

## Vorschlag

Module werden auf einer Leiter eingeordnet, ausschließlich aus dem Code abgeleitet:

```
asserted > tested > reachable > claimed-only > stub > synthetic-risk
```

- **asserted:** nur behauptet (Docstring/Kommentar).
- **tested:** Test existiert und läuft.
- **reachable:** Aufrufpfad vom Entry-Point nachweisbar.
- **claimed-only:** Verhalten behauptet, weder Test noch Reachability.
- **stub:** Signatur ohne Implementierung.
- **synthetic-risk:** Funktion gibt Random-/Konstant-Werte zurück, wo eine Rechnung behauptet wird — neues scharfes Signal.

Prinzip: **under-credits, never over-credits** — die Einordnung kann Code unterschätzen, nie über beweisbare Evidenz hinaus anrechnen.

## Integration

- Die Leiter ist eine **Gesamtmetrik/Report-Zeile** je Modul, kein weiterer Score (adr/0006-konform).
- `synthetic-risk` qualifiziert als Kandidat für `critical`-Tier (#55 `signalSeverity`) und damit Hard-Gate; Eigenes Signal-Issue mit 3/3/2-Fixtures vor Promotion (SIGNAL-DoD).
- Code-Achse (`signals.code`) um `verificationLadder`-Metadaten je Indicator erweitern — eigene Changeset, nicht hier.
