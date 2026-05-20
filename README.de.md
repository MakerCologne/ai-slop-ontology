# AI Slop Ontologie

**Sprachen:** [English (kanonisch)](README.md) · Deutsch

Eine strukturierte, agentenkonsumierbare Wissensbasis über das Phänomen *AI Slop*. Konsolidiert aus akademischer Forschung (Shaib et al. 2025; Madsen & Puyt 2025; Shumailov et al. 2024), investigativem Journalismus (404 Media; NYT; Guardian), Industrieforschung (NewsGuard; Pangram Labs) und Lexikographie (Merriam-Webster 2025; Oxford 2024).

**Version:** 1.0.0 | **Stand:** 2026-05-20 | **Lizenz:** CC BY 4.0

> ℹ️ **Hinweis zur Internationalisierung:** Die Dokumentation liegt in englischer (kanonischer) und deutscher Fassung vor. Code-nahe Artefakte (`ai_slop_ontology.yaml`, `ontology.json`, `ontology.ttl`, `src/`) sind ausschließlich auf Englisch geführt — Klassennamen, Property-Namen und Schwellenwerte sind in Agenten- und Tool-Kontexten verbindlich englisch. Übersetzungen in `docs/de/` spiegeln die englische Quelle und können gegenüber `docs/en/` zeitweise hinterherhängen.

## Was ist AI Slop?

AI Slop ist **nicht** einfach "KI-generierter Content". Es ist ein **Risikoprofil**. Drei notwendige Bedingungen müssen ALLE erfüllt sein:

1. **Generative KI ist die primäre Quelle** des Inhalts
2. **Menschliche Sorgfalt, Kuration oder Verifikation fehlt**
3. **Inhalt wird unverlangt distribuiert** (Push, nicht Pull)

Kernerkenntnis: Sorgfältig kuratierte, geprüfte und intentional veröffentlichte KI-Outputs sind ausdrücklich KEIN Slop.

## Quick Start

```python
import json, yaml

# Kanonische Ontologie laden
with open("ai_slop_ontology.yaml") as f:
    ontology = yaml.safe_load(f)

# Inhalt klassifizieren
slop_score = compute_slop_score(content, modality)
if slop_score >= 0.70:
    action = "exclude_from_rag"
elif slop_score >= 0.40:
    action = "require_human_review"
else:
    action = "allow_with_checks"
```

## Repository-Struktur

```
├── README.md                     ← Englischer Einstieg
├── README.de.md                  ← Diese Datei (deutscher Einstieg)
├── ai_slop_ontology.yaml         ← Maschinenlesbare YAML-Ontologie
├── ontology.json                  ← Agentenfreundliches JSON (alle Daten)
├── ontology.ttl                   ← RDF/Turtle (Semantic Web)
├── docs/
│   ├── en/                        ← Englische Dokumentation (kanonisch)
│   └── de/                        ← Deutsche Dokumentation
├── skills/
│   └── ai-slop-detection/         ← Agent-Skill (englisch)
├── src/
│   ├── classifier.py              ← Python-Klassifikator
│   └── scorer.py                   ← Scoring-Engine
└── examples/                       ← Bewertete Beispiele (JSON)
```

## Klassifikationsschwellen

| Score | Klasse | Agentenverhalten |
|-------|--------|------------------|
| 0.00–0.24 | LowSlopRisk | Normale Nutzung, Quellenprüfung weiterhin nötig |
| 0.25–0.49 | ModerateSlopRisk | Nur mit Gegenprüfung verwenden |
| 0.50–0.69 | HighSlopRisk | Nicht als Hauptquelle, Human Review |
| 0.70–1.00 | AISlopCandidate | Nicht zitieren, nicht als Fakt speichern |
| beliebig + hoher Schaden | CriticalReviewRequired | Immer eskalieren (Recht, Medizin, Kinder) |

## Scoring-Formel

```
weights = {critical: 1.0, high: 0.7, medium: 0.4, low: 0.2}
slop_score = min(1.0, sum(weights[s.severity] * s.confidence) / max(1, n))
is_slop = (slop_score >= 0.4) ODER (irgendein critical) ODER (≥ 2 high severity)
```

## Wichtige deutsche Dokumente

- [`docs/de/ai-slop-ontology-v1.0.0.md`](docs/de/ai-slop-ontology-v1.0.0.md) — Kanonisches Dokument (526 Zeilen, 14 Abschnitte)
- [`docs/de/ontology.md`](docs/de/ontology.md) — Menschenlesbare Taxonomie-Übersicht
- [`docs/de/ontology-structure.md`](docs/de/ontology-structure.md) — Property-basiertes Modell und Klassenhierarchie
- [`docs/de/references.md`](docs/de/references.md) — Quellenliste (30 Referenzen)
- [`docs/de/research-v0.1.md`](docs/de/research-v0.1.md) — Forschungsergebnisse v0.1
- [`docs/de/report.md`](docs/de/report.md) — Deep-Research-Report (Runde 1)
- [`docs/de/report-extended.md`](docs/de/report-extended.md) — Erweiterte Forschung (Runde 2)

## 12 Schadenstypen

Model Collapse, Epistemische Verschmutzung, Misinformation, Vertrauenserosion, Workplace-Produktivitätsverlust, Creator-Squeeze, Schaden an Kindern, Ad-Fraud, Kognitive Last, Umweltkosten, Demokratie-Risiko, Royalty-Fraud

## Agent-Integration

```python
def classify_content(content, modality) -> SlopAssessment:
    """Liefert: {slop_score, is_slop, dimensions, harms, actor_hypothesis}"""

def route_by_harm(assessment) -> Action:
    """Block | Refine | Flag | Pass"""

def update_ontology(new_evidence) -> None:
    """Erweitern um neue Actor-Patterns, Harm-Typen, Detection-Methoden"""
```

Kompatibel mit: LangGraph-Node, MCP-Tool, AutoGen-Function

## Pflege

- **Update-Rhythmus:** Quartalsweise (neue Modellgenerationen → neue Slop-Patterns)
- **Ad-hoc:** Neue NewsGuard-Quartalsberichte, neue arXiv-Taxonomien
- **Ground Truth:** [github.com/cshaib/slop](https://github.com/cshaib/slop)
- **Beiträge willkommen:** Audio-Slop-Forschung, nicht-westliche Plattformen, Cross-Modal-Detection

## Lizenz

CC BY 4.0
