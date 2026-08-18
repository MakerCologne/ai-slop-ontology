# AI-Slop-Ontologie

**Sprachen:** [English (kanonisch)](README.md) · Deutsch

Eine strukturierte, agentenlesbare Wissensbasis über das Phänomen *AI Slop*. Sie verbindet akademische Forschung, investigativen Journalismus, Branchenanalysen und maschinenlesbare Klassifikationsregeln.

**Version:** 1.2.1 | **Stand:** 10. Juli 2026 | **Lizenz:** CC BY 4.0

> **Sprachmodell:** Englisch ist für Code, Klassen, Properties, YAML, JSON und RDF kanonisch. Die deutsche Dokumentation bildet den aktuellen fachlichen Stand ab. Technische Bezeichner bleiben unverändert englisch, damit Agenten und Integrationen sprachübergreifend kompatibel bleiben.

## Schnellstart

```python
import yaml

with open("ai_slop_ontology.yaml") as f:
    ontology = yaml.safe_load(f)

slop_score = compute_slop_score(content, modality)
if slop_score >= 0.70:
    action = "exclude_from_rag"
elif slop_score >= 0.40:
    action = "require_human_review"
else:
    action = "allow_with_checks"
```

## CLI-Toolkit (`slop`)

Eine Kommandozeile über dieselbe Engine und dieselben Ontologie-Daten. Ohne
Fremd-Abhängigkeiten — der Detektor nutzt nur die Standardbibliothek.

```bash
pip install .             # stellt den Befehl `slop` überall bereit
pip install -e .          # oder editierbar aus einem Checkout (bzw. `python -m slopkit`)

slop score "In today's rapidly evolving landscape, our holistic platform serves as a hub."
slop classify --file entwurf.md        # Slop-Typen, Signale, Dimensionen, Maßnahmen
slop rhetoric "It's not a tool. It's a movement."   # benannte KI-Schreibmuster
echo "Text" | slop check -             # Score plus Rhetorik-Report (stdin)
slop code --lang python app.py         # Slop-Muster im Quellcode
slop info                              # Metadaten zu Signaldatenbank und Ontologie
slop benchmark                         # Benchmark gegen den gelabelten Korpus
slop selfcheck                         # Konsistenzprüfung JSON/TTL/YAML/Skill
```

| Befehl | Ausgabe |
|---|---|
| `score` | numerischer Slop-Score (0–1) plus Schweregrad |
| `classify` | vollständiger Report: Slop-Typen, gewichtete Signale, Dimensionen, Gegenmaßnahmen |
| `rhetoric` | rhetorische Muster als benannte Evidenz, bewusst ohne Score |
| `check` | `classify` und `rhetoric` in einem Durchlauf |
| `code` | Code-Slop: halluzinierte Pakete, hartkodierte Secrets, Kommentar-Wildwuchs |
| `info` / `benchmark` / `selfcheck` | Metadaten / Evaluation / Konsistenz |

Jeder Textbefehl liest Positionsargument, `--file PFAD` oder stdin (`-`) und
kennt `--json` für maschinenlesbare Ausgabe. `score` und `check` kennen
zusätzlich `--fail-over SCHWELLE` und liefern Exit-Code 1 darüber — gedacht als
CI-Gate.

Das Wheel enthält Engine, Agenten-Skill und `ontology.json`; die Scoring-Befehle
laufen daher auch außerhalb eines Checkouts. `benchmark` und `selfcheck` nutzen
Repo-Werkzeuge (Korpus, drei Serialisierungen) und brauchen einen Checkout —
`SLOP_REPO_ROOT` darauf zeigen lassen oder im Repo ausführen.

Die vollständige Anleitung mit Anwendungsfällen und getesteten Beispielen steht
in [`docs/USER-GUIDE.md`](docs/USER-GUIDE.md) (englisch, kanonisch).

## Was ist AI Slop?

AI Slop ist **nicht einfach KI-generierter Inhalt**, sondern ein **Risikoprofil**. Drei notwendige Bedingungen müssen gemeinsam erfüllt sein:

1. Generative KI ist die primäre Quelle.
2. Menschliche Sorgfalt, Kuration oder Verifikation fehlt.
3. Der Inhalt wird unverlangt verbreitet oder veröffentlicht – Push statt Pull.

Sorgfältig kuratierte, überprüfte und absichtlich veröffentlichte KI-Hilfsoutputs sind ausdrücklich **kein** Slop.

## Dokumentation

```text
├── README.md                         Englischer Einstieg, kanonisch
├── README.de.md                      Deutscher Einstieg
├── docs/
│   ├── USER-GUIDE.md                 Vollständige CLI-Anleitung, englisch
│   ├── en/                           Englische Dokumentation
│   └── de/                           Deutsche Dokumentation
├── AI-SLOP-ONTOLOGY.md               Kanonisches Fachmodell, Version 1.2.1
├── ai_slop_ontology.yaml             Maschinenlesbare YAML-Ontologie
├── ontology.json                     Agentenfreundliches JSON
├── ontology.ttl                      RDF/Turtle
├── slopkit/                          CLI-Toolkit, Entry-Point `slop`
├── src/                              Klassifikator und Scoring-Engine
├── skills/ai-slop-detection/         Agenten-Skill, eigenständig lauffähig
├── tests/                            Unit-Tests (`python -m unittest discover tests`)
├── extensions/human-work-seo-slop/   Human-, Work-, Management- und SEO-Slop
└── integrations/ontology-playground/ Microsoft-Ontology-Playground-Adapter
```

Die aktuelle deutsche Dokumentation beginnt unter [`docs/de/`](docs/de/). Ältere Forschungsberichte bleiben erhalten, sind dort aber klar als historische Arbeitsstände gekennzeichnet.

## Experimentelle Erweiterung: Human, Work, Management und SEO Slop

Die Erweiterung unter `extensions/human-work-seo-slop/` ergänzt die AI-Slop-Ontologie technologieunabhängig, ohne die kanonische AI-Slop-Definition zu verändern.

Sie enthält:

- `HumanSlop`, `WorkSlopFamily` und `SEOSlop` als Gruppierungsbegriffe,
- 27 konkrete Typen,
- 11 querschnittliche Bewertungsdimensionen,
- sieben SEO-Slop-Untertypen,
- Quellenstatus wie `established`, `emerging`, `grounded_extension` und `candidate`,
- verbindliche Regeln gegen Fehlklassifikationen.

Der etablierte Begriff **Workslop** behält seine enge Bedeutung für KI-generierte Arbeitsinhalte und wird als `AIWorkslop` geführt. `WorkSlopFamily` ist die separate technologieunabhängige Oberkategorie.

Wichtige Typen:

- `HumanWorkSlop`
- `ManagementSlop`
- `StrategySlop`
- `JargonSlop`
- `MeetingSlop`
- `DecisionSlop`
- `MetricsSlop`
- `ProcessSlop`
- `AdministrativeSlop`
- `ComplianceSlop`
- `CommunicationSlop`
- `DocumentationSlop`
- `PresentationSlop`
- `CoordinationSlop`
- `ReviewSlop`
- `OpenSourceContributionSlop`
- `HiringSlop`
- `EducationalSlop`
- `Slopaganda`

Eine Klassifikation gilt für **Artefakte, Aktivitäten, Prozesse oder Systeme**, niemals pauschal für Menschen. KI-Nutzung, menschliche Autorschaft, Jargon, Länge, Aufwand oder eine unpopuläre Entscheidung reichen allein nicht aus.

## Microsoft Ontology Playground

Unter `integrations/ontology-playground/` liegen sieben importierbare RDF/XML-Ansichten:

1. `ai-slop-core`
2. `ai-slop-media`
3. `ai-slop-domains`
4. `ai-slop-intent`
5. `work-slop`
6. `management-slop`
7. `seo-slop`

Jeder Katalogeintrag enthält `ontology.rdf` und `metadata.json`. Ein eigener Validator prüft XML, Metadaten, Entitätszahlen, Identifier, Beziehungen und Manifest-Konsistenz.

## Ontologie-Architektur

### Oberste Klassen

```text
ContentItem → SyntheticContent → AI_SlopCandidate → ConfirmedAI_Slop
```

Zentrale Properties:

- `hasGenerationMode`
- `hasHumanOversightLevel`
- `hasQualityProfile`
- `hasDistributionPattern`
- `hasIntent`
- `hasProvenanceStatus`
- `hasRiskProfile`
- `hasSlopScore`

### Klassifikationsschwellen

| Score | Klasse | Verhalten |
|---|---|---|
| 0,00–0,24 | `LowSlopRisk` | Normal verwenden, Quellen weiterhin prüfen |
| 0,25–0,49 | `ModerateSlopRisk` | Nur mit Gegenprüfung verwenden |
| 0,50–0,69 | `HighSlopRisk` | Nicht als Hauptquelle, menschliche Prüfung |
| 0,70–1,00 | `AISlopCandidate` | Nicht zitieren und nicht als Fakt speichern |
| beliebig + hoher Schaden | `CriticalReviewRequired` | Immer eskalieren |

### Scoring seit Version 1.2.0

```text
weights = {critical: 1.0, high: 0.7, medium: 0.4, low: 0.2}
slop_score = min(1.0, 1 − Π(1 − weights[s.severity] * s.confidence))
is_slop = (slop_score >= 0.4) OR (any critical) OR (≥ 2 high severity)
```

Unabhängige Hinweise sammeln sich mit Noisy-OR an, statt durch Mittelwertbildung abgeschwächt zu werden.

## Qualitätsdimensionen

Nach Shaib et al. 2025:

- **Informationsnutzen:** Dichte und Relevanz
- **Informationsqualität:** Faktizität und Verzerrung
- **Stilqualität:** Wiederholung, Schablonenhaftigkeit, Kohärenz, Flüssigkeit, Länge, Wortkomplexität und Ton

Systemische 7V-Dimensionen nach Madsen und Puyt:

`Volume`, `Velocity`, `Variety`, `Value`, `Verification`, `Visibility`, `Virality`

## Neuerungen

### Version 1.2.x

- gelabelter Evaluationskorpus mit 53 Beispielen in sieben Sprachen,
- Benchmark- und Kalibrierungswerkzeuge,
- F1-Anstieg der Skill-Pipeline von 0,47 auf 0,98 bei Präzision 1,0,
- Noisy-OR-Aggregation,
- zusätzliche Marker für Hindi, Vietnamesisch und Urdu,
- Konsistenzprüfung für YAML, JSON und Turtle,
- Paritätstests zwischen den Klassifikations-Engines,
- neun rhetorische Muster als benannte Detektoren, bewusst ohne Score,
- CLI-Toolkit `slop` mit CI-Gating über `--fail-over`,
- Human-/Work-/Management-/SEO-Slop-Erweiterung,
- Microsoft-Ontology-Playground-Adapter,
- deutsche Parallel-Dokumentation unter `docs/de/`.

### Version 1.1.x

- `SecurityReportSlop`,
- `PeerReviewSlop`,
- Bildsignal `HyperTypicality`,
- Wortgrenzen- und Überlappungsbereinigung,
- neutralere Burstiness-Bewertung kurzer Texte,
- Schweregrad-gewichtetes Scoring,
- Test-Suite, Lizenz und Changelog.

## Zwölf Schadenstypen

Model Collapse, epistemische Verschmutzung, Desinformation, Vertrauenserosion, Produktivitätsverlust am Arbeitsplatz, Creator Squeeze, Schaden für Kinder, Werbebetrug, kognitive Belastung, Umweltkosten, Demokratierisiko und Royalty Fraud.

## Agenten-Integration

```python
def classify_content(content, modality) -> SlopAssessment:
    """Liefert slop_score, is_slop, dimensions, harms und actor_hypothesis."""

def route_by_harm(assessment) -> Action:
    """Block | Refine | Flag | Pass"""

def update_ontology(new_evidence) -> None:
    """Erweitert Muster, Schäden und Erkennungsmethoden."""
```

Kompatibel mit LangGraph, MCP und AutoGen.

## Pflege

- regulär quartalsweise,
- zusätzlich bei neuen relevanten Taxonomien oder Plattformänderungen,
- Ground Truth: `github.com/cshaib/slop`,
- Beiträge zu Audio Slop, nichtwestlichen Plattformen und multimodaler Erkennung sind willkommen.

## Lizenz

CC BY 4.0
