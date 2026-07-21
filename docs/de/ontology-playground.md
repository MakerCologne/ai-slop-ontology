# Microsoft Ontology Playground Adapter

**Stand:** 21. Juli 2026  
**Quellverzeichnis:** `integrations/ontology-playground/`

Der Adapter stellt kompakte RDF/XML-Ansichten der AI-Slop-Ontologie bereit. Die vollständige JSON-, YAML- und Turtle-Ontologie bleibt die fachliche Quelle. Die Playground-Dateien sind reduzierte Projektionen für verständliche, interaktive Graphen.

## Katalogeinträge

| Slug | Inhalt | Entitäten |
|---|---|---:|
| `ai-slop-core` | AI Slop, Human Slop, Work Slop, SEO Slop, Evidenz, Schäden und Maßnahmen | 8 |
| `ai-slop-media` | Text, Bild, Video, Audio, Musik, Code und multimodaler Slop | 8 |
| `ai-slop-domains` | Academic, Legal, AI Workslop, Peer Review, Security Report, Educational und Political Slop | 8 |
| `ai-slop-intent` | Engagement, Monetarisierung, Propaganda, Recommendation Poisoning, Search Manipulation, Impersonation und Placeholder Publishing | 8 |
| `work-slop` | AI Workslop, menschlich erzeugter Work Slop und Management Slop | 4 |
| `management-slop` | Strategy, Jargon, Meeting, Decision, Metrics, Administrative und Compliance Slop | 8 |
| `seo-slop` | sieben technologieunabhängige SEO-Slop-Typen | 8 |

## Struktur

```text
integrations/ontology-playground/
├── README.md
├── manifest.json
├── validate_adapter.py
└── catalogue/community/hikaman/
    ├── ai-slop-core/
    ├── ai-slop-media/
    ├── ai-slop-domains/
    ├── ai-slop-intent/
    ├── work-slop/
    ├── management-slop/
    └── seo-slop/
```

Jeder Katalogordner enthält:

```text
ontology.rdf
metadata.json
```

## Modellierung

Das Playground stellt `owl:ObjectProperty`-Beziehungen mit Domain, Range und Kardinalität sichtbar dar. Deshalb ergänzt der Adapter explizite Kanten wie:

- `isSubtypeOf`
- `supports`
- `causes`
- `mitigates`
- `canOverlapWith`
- `combines`
- `canProduce`
- `canDistort`

Jede Entität besitzt genau eine Identifier-Property, eine kurze Beschreibung, ein Icon und eine Farbe. Gemeinsame Begriffs-URIs halten die Teilmodelle logisch zusammen.

## Warum mehrere Graphen?

Die Ontologie besitzt unabhängige Achsen für Medium, Domäne, Zweck, Erzeugungsart, organisatorische Form, Schäden und Maßnahmen. Ein einzelner Graph mit allen Klassen wäre schwer lesbar. Die sieben Ansichten halten jeweils einen fachlichen Blickwinkel klein.

## Validierung

Vom Repository-Root aus:

```bash
python3 integrations/ontology-playground/validate_adapter.py
python3 -m unittest tests.test_ontology_playground_adapter
```

Geprüft werden:

1. `ontology.rdf` und `metadata.json`,
2. gültiges XML,
3. Metadatenfelder und Kategorien,
4. drei bis acht Klassen pro Eintrag,
5. Übereinstimmung mit dem Manifest,
6. genau ein Identifier je Entität,
7. lokale Domain- und Range-Endpunkte.

Die Tests laufen auch in GitHub Actions.

## Upstream-Einreichung

In einem Fork von Microsoft Ontology Playground werden die sieben Ordner nach

```text
catalogue/community/hikaman/
```

kopiert. Danach:

```bash
npm run catalogue:build
npm run validate
npm test
npm run build
```

Anschließend kann der Pull Request an `microsoft/Ontology-Playground` geöffnet werden.

## Schutzregel

Ein Graphknoten bezeichnet einen beobachteten Slop-Typ, keine Person. Menschliche Autorschaft, KI-Nutzung, Jargon, Aufwand oder Unbequemlichkeit reichen allein niemals für eine Klassifikation aus.
