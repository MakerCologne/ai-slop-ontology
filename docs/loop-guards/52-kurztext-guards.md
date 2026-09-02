# Kurztext-/Längen-Guards (#52)

**Status:** spec · **Verwandt:** #21/#24 (Metriken mit Mindestlängen), doctrine-Feld in punctuation.indicators

## Mindestlängen je Metrik

| Metrik | Mindestlänge | Verhalten darunter |
|---|---|---|
| UniformSentenceLength (std_dev) | 3 Sätze / 40 Wörter | skip (kein Befund, Feld `skipped: short_text`) |
| Burstiness / rhythm metrics | 5 Sätze | skip |
| per-500-words-Normalisierungen | 120 Wörter | skaliert auf 100 Wörter mit Konfidenz-Abschlag 0.2, Report-Flag `scaled: true` |
| Em-Dash/ellipsis/exclamation pro Satz | 3 Sätze | skip |
| hedging/phrases-Zählung | 50 Wörter | zählen, aber confidence 0.5-fach |

Definiertes Verhalten für Tweets/Commits/Titel: score bleibt 0-Anteilig leer; Report zeigt `short_text: true` statt fehlender Signale. Fixtures: 5-/20-/50-Wort-Texte (je 2) in `tests/test_short_text_guards.py` (Implementierung folgt im Loop-Issue).
