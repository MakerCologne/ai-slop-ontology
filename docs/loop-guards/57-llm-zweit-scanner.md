# LLM-Zweit-Scanner (Layer 2) (#57)

**Status:** spec · **Verwandt:** adr/0001, Swiss-Cheese-Modell, Bias-Quellen: MT-Bench (arXiv:2306.05685), Huang et al. (arXiv:2310.01798)

## Vertrag

- `llm_scanner.py` als **Layer 2** gegen `detection-signals.md`: nur Veto/ergänzender Befund mit zitiertem Textabschnitt, **nie alleiniges Abbruchkriterium**.
- **Prompt-Rotation:** Signal-Reihenfolge und Frageform rotieren über definierte Varianten (mindestens 3).
- **Position-Swap:** Befunde werden in beiden Reihenfolgen geprüft; Instabilität → Befund downgrade auf „unsicher" statt Fix-Trigger.

## Akzeptanz

Bias-Test: vertauschte Signal-Positionen liefern stabile Befunde (Übereinstimmung ≥ 90 % auf dem Control-Set, adr/0003); ohne externes Feedback keine Selbstkorrektur-Runden.
