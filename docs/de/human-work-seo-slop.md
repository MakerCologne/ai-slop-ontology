# Human, Work, Management und SEO Slop

**Status:** experimentelle Erweiterung  
**Version:** 0.1.0  
**Stand:** 21. Juli 2026  
**Kanonische Dateien:** `extensions/human-work-seo-slop/`

## Zweck

Diese Erweiterung ergänzt die AI-Slop-Ontologie um technologieunabhängige Formen von Slop in Arbeitsorganisation, Management und Suchmaschinen- beziehungsweise Answer-Engine-Optimierung.

Sie verändert die enge kanonische Definition von **AI Slop** nicht. Insbesondere bleibt **Workslop** in seiner etablierten Bedeutung ein Begriff für KI-generierte Arbeitsinhalte, die brauchbar oder vollständig wirken, aber die eigentliche Denk-, Prüf- und Aufräumarbeit auf Empfänger verlagern. Dieser Typ heißt in der Erweiterung `AIWorkslop`.

## Begriffsstatus

| Begriff | Status | Einordnung |
|---|---|---|
| `AIWorkslop` | etabliert | durch BetterUp Labs und Stanford Social Media Lab definiert und empirisch untersucht |
| `HumanSlop` | begründete Erweiterung | vorgeschlagener Oberbegriff, kein etablierter wissenschaftlicher Terminus |
| `HumanWorkSlop` | begründete Erweiterung | trennt menschliche Erzeugung von der Arbeitsform |
| `ManagementSlop` | begründete Erweiterung | basiert auf Forschung zu organisatorischem Bullshit, Red Tape, administrativer Last und Meeting-Effektivität |
| `SEOSlop` | begründete Erweiterung | technologieunabhängig, an offiziellen Suchmaschinen-Spamkategorien ausgerichtet |
| `HiringSlop` | aufkommend | aktuelle Verwendung für generische und massenhaft optimierte Bewerbungen |
| `OpenSourceContributionSlop` | aufkommend | empirische Forschung beschreibt den Belastungseffekt als AI-DDoS |
| `EducationalSlop` | etablierte Domänenverwendung | peer-reviewte Operationalisierung in Bildungsinhalten |
| `Slopaganda` | aufkommendes Forschungskonzept | KI-Propaganda durch Überflutung und Kontextzerfall |

## Gemeinsamer Mechanismus

Eine schlechte oder unbeliebte Arbeit ist nicht automatisch Slop. Ein Kandidat benötigt eine Kombination mehrerer Merkmale:

1. **Oberflächliche Kompetenz:** Das Ergebnis wirkt seriös, vollständig oder professionell.
2. **Geringer Zielbeitrag:** Es trägt wenig zum angegebenen Zweck bei.
3. **Aufwandsverlagerung:** Prüfung, Interpretation, Koordination oder Reparatur wird auf andere übertragen.
4. **Verstärkung:** Das Ergebnis wird angeordnet, wiederholt, skaliert oder durch ein Verteilungssystem bevorzugt.

## Ontologisches Modell

```text
SlopLikePhenomenon
├── AISlop
├── HumanSlop
│   └── HumanWorkSlop
├── WorkSlopFamily
│   ├── AIWorkslop
│   ├── HumanWorkSlop
│   ├── ManagementSlop
│   │   ├── StrategySlop
│   │   ├── JargonSlop
│   │   ├── MeetingSlop
│   │   ├── DecisionSlop
│   │   ├── MetricsSlop
│   │   ├── ProcessSlop
│   │   ├── AdministrativeSlop
│   │   └── ComplianceSlop
│   ├── CommunicationSlop
│   │   ├── DocumentationSlop
│   │   └── PresentationSlop
│   ├── CoordinationSlop
│   ├── ReviewSlop
│   ├── HiringSlop
│   └── OpenSourceContributionSlop
├── SEOSlop
│   ├── ScaledContentSlop
│   ├── DoorwayPageSlop
│   ├── SiteReputationSlop
│   ├── ExpiredDomainSlop
│   ├── ScrapedRemixSlop
│   ├── SearchSaturationSlop
│   └── GEOManipulationSlop
├── EducationalSlop
└── Slopaganda
```

Die Hierarchie ist absichtlich mehrfach zuordenbar. Eine KI-erzeugte Management-Präsentation kann gleichzeitig `AIWorkslop`, `ManagementSlop` und `PresentationSlop` sein. Eine menschlich geschriebene Matrix aus Stadtseiten kann zugleich `HumanSlop`, `SEOSlop` und `DoorwayPageSlop` sein.

## Work Slop

### AI Workslop

`AIWorkslop` bezeichnet KI-generierte Arbeitsinhalte, die professionell aussehen, aber Kontext, Substanz oder Nutzbarkeit vermissen lassen. Empfänger müssen die fehlende Denk- und Prüfleistung nachholen.

Die 2025 veröffentlichte Untersuchung von BetterUp Labs und Stanford Social Media Lab berichtete, dass etwa 40 Prozent der befragten Büroangestellten im vorherigen Monat Workslop erhalten hatten. Die Bearbeitung eines Vorfalls verursachte im Mittel ungefähr zwei Stunden Zusatzaufwand.

### Human Work Slop

`HumanWorkSlop` erfasst denselben Mechanismus, wenn Menschen die primäre Quelle oder die fortlaufenden Maintainer sind. Beispiele:

- wiederkehrende Berichte, die lediglich bestehende Tracker kopieren,
- Statusdokumente ohne klaren Empfänger oder Entscheidungswert,
- manuell erzeugte Ausgaben, die nur eine Aktivitätskennzahl erfüllen,
- Prüfungen, die Verantwortung darstellen, aber keine Evidenz bewerten.

Der Begriff darf niemals als pauschale Bezeichnung für Kollegen oder Berufsgruppen verwendet werden.

## Management Slop

Management Slop ist besonders relevant, weil Management formale Macht besitzt, Inhalte und Rituale zu verpflichtenden, wiederkehrenden Kosten zu machen.

### Forschungshintergrund

- Forschung zu **organisatorischem Bullshit** untersucht Kommunikation mit Gleichgültigkeit gegenüber Wahrheit und praktischer Bedeutung.
- **Red Tape** beschreibt Regeln, die Ressourcen verbrauchen, ohne legitime Ziele angemessen zu unterstützen.
- **Administrative Burden** zerlegt Belastung in Lern-, Erfüllungs- und psychologische Kosten.
- Modelle zu **administrativer Aufblähung** zeigen, wie früher sinnvolle Prozesse veralten und dennoch bestehen bleiben.
- Meeting-Forschung bewertet Effektivität anhand erreichter Ziele, Teilnehmerwahl und Entscheidungsfolgen.
- Goodharts Gesetz erklärt, warum ein Proxy seine Aussagekraft verliert, sobald er zum optimierten Ziel wird.

### Untertypen

| Typ | Kernproblem | Typische Signale |
|---|---|---|
| `StrategySlop` | Richtung ohne echte Entscheidungen | keine Prioritäten, Ressourcen, Trade-offs oder prüfbaren Annahmen |
| `JargonSlop` | eindrucksvolle Sprache ohne operative Bedeutung | undefinierte Schlagwörter, strategische Mehrdeutigkeit, Autorität durch Ton |
| `MeetingSlop` | synchrone Kosten ohne angemessene Zielerreichung | kein Ziel, falsche Teilnehmer, Statusvorlesen, kein Beschluss oder Owner |
| `DecisionSlop` | Darstellung von Entschlossenheit ohne Verpflichtung | keine Kriterien, Evidenz, Zuständigkeit oder Dokumentation |
| `MetricsSlop` | Proxy-Optimierung ersetzt das eigentliche Ziel | Vanity Metrics, Aktivitätsquoten, Dashboard-Wachstum, Gaming |
| `ProcessSlop` | veraltete oder doppelte Abläufe bleiben bestehen | kein Owner, keine Sunset-Regel, doppelte Freigaben, Ritualberichte |
| `AdministrativeSlop` | Aufwand ist gegenüber dem legitimen Ziel unverhältnismäßig | wiederholte Nachweise, undurchsichtige Formulare, ausgelagerte Belastung |
| `ComplianceSlop` | Nachweis von Kontrolle ersetzt Risikosenkung | Checkbox-Nachweise, doppelte Bestätigungen, Audit-Theater |

### Keine ausreichenden Belege

- Eine Entscheidung ist unpopulär.
- Ein Prozess ist langsam oder lästig.
- Eine Kontrolle erzeugt Arbeit.
- Ein Meeting dauert lange.
- Eine Strategie enthält Unsicherheit.
- Eine Kennzahl ist unvollkommen.

Sicherheits-, Rechts-, Datenschutz-, Barrierefreiheits-, Audit- und Funktionstrennungskontrollen können belastend und dennoch legitim sein. Eine Slop-Klassifikation benötigt belegte Unverhältnismäßigkeit, geringen Zielbeitrag und Aufwandsverlagerung.

## Kommunikations- und Koordinationsformen

### `CommunicationSlop`

Kommunikation erzeugt mehr Interpretations- und Antwortarbeit als gemeinsames Verständnis.

### `DocumentationSlop`

Dokumentation wirkt vollständig, ist aber veraltet, widersprüchlich, ohne Owner oder nicht für die tatsächliche Nutzung geschrieben.

### `PresentationSlop`

Eine Präsentation erzeugt den Eindruck von Klarheit und Fortschritt, enthält aber keine nachvollziehbare Evidenz, Entscheidung oder Handlung.

### `CoordinationSlop`

Synchronisations-, Übergabe- und Abstimmungsmechanismen kosten mehr, als sie an Abhängigkeit oder Unsicherheit auflösen.

### `ReviewSlop`

Eine Prüfung erfüllt formal eine Kontrollfunktion, setzt sich aber nicht substanziell mit Evidenz, Zweck oder Folgen auseinander.

## SEO Slop

SEO Slop ist such- oder antwortmaschinenorientierter Inhalt beziehungsweise eine Seitenstruktur, deren Hauptfunktion Ranking oder Sichtbarkeit ist, während der eigenständige Nutzwert gering bleibt.

Die Kategorie ist technologieunabhängig. Ein vollständig menschlich erstelltes Netzwerk aus Doorway Pages kann ebenso SEO Slop sein wie eine KI-erzeugte Content-Farm.

### Untertypen

| Typ | Beschreibung |
|---|---|
| `ScaledContentSlop` | große Mengen geringwertiger Seiten, hauptsächlich zur Ranking-Manipulation |
| `DoorwayPageSlop` | sehr ähnliche Seiten für verwandte Suchanfragen, die zu einem anderen Ziel weiterleiten |
| `SiteReputationSlop` | thematisch losgelöste Inhalte nutzen die Autorität einer etablierten Domain |
| `ExpiredDomainSlop` | eine abgelaufene Domain wird zur Ausnutzung alter Reputation oder Links umgenutzt |
| `ScrapedRemixSlop` | gescrapte, übersetzte, zusammengesetzte oder leicht umformulierte Inhalte ohne wesentlichen Mehrwert |
| `SearchSaturationSlop` | koordinierte Seiten oder Domains besetzen möglichst viele Such- oder Retrieval-Ergebnisse |
| `GEOManipulationSlop` | Inhalte werden primär zur Beeinflussung generativer Such- und Antwortsysteme erstellt |

### Abgrenzung

Skalierung ist nicht automatisch Slop. Produktkataloge, Nachschlagewerke, lokale Behördeninformationen und automatisch erzeugte Statusseiten können großen Umfang und hohen Nutzwert haben. Entscheidend sind Ranking-Manipulation, fehlende Originalität, schwache Zweckorientierung und systematische Überflutung.

## Weitere Typen

### Open Source Contribution Slop

Minderwertige Issues, Pull Requests, Reviews oder Sicherheitsberichte können Maintainer-Zeit überproportional verbrauchen. Der Typ verlangt konkrete Merkmale wie fehlende Reproduzierbarkeit, unzutreffende Codebezüge, generische Änderungsvorschläge oder massenhafte Einreichung.

### Hiring Slop

Generische, massenhaft erzeugte oder stark optimierte Bewerbungen können das Kandidatensignal verschlechtern und Prüflast auf Arbeitgeber verlagern. Der Begriff bleibt `emerging`, weil Grenzen und Forschung noch nicht stabil genug sind.

### Educational Slop

Bildungsinhalte, die autoritative Lehre imitieren, aber fachliche oder didaktische Mindestanforderungen verfehlen.

### Slopaganda

Ideologische KI-Masseninhalte, deren Wirkung nicht nur auf einzelnen Falschbehauptungen, sondern auch auf Überflutung, Wiederholung, Kontextzerfall und kognitiver Erschöpfung beruht.

## Querschnittliche Dimensionen

Die maschinenlesbare Erweiterung bewertet unter anderem:

- `goal_contribution_deficit`
- `recipient_effort_transfer`
- `superficial_competence`
- `actionability_deficit`
- `verification_deficit`
- `coordination_overhead`
- `process_obsolescence`
- `metric_gaming`
- `truth_indifference`
- `distribution_manipulation`
- `scale_amplification`

## Fehlklassifikationsregeln

1. Klassifiziert werden Artefakte, Aktivitäten, Prozesse und Systeme – nicht Menschen.
2. KI-Nutzung allein ist kein Beleg.
3. Menschliche Autorschaft allein ist kein Beleg.
4. Jargon, Länge, Formalität oder Unbeliebtheit allein sind kein Beleg.
5. Ein legitimer Schutz- oder Kontrollzweck muss gegen den Aufwand abgewogen werden.
6. Private Entwürfe und klar gekennzeichnete Arbeitsstände sind nicht automatisch Slop.
7. Kandidatenbegriffe bleiben unpromotet, solange Grenzen und Evidenz nicht tragfähig sind.

## Dateien und Tests

```text
extensions/human-work-seo-slop/
├── README.md
├── RESEARCH.md
├── human_work_seo_slop.json
├── human_work_seo_slop.ttl
└── examples.json
```

Tests:

```bash
python3 -m unittest tests.test_human_work_seo_extension
```

Die Tests prüfen Struktur, Typstatus, Pflichtfelder, Beispiele, Gegenbeispiele und Schutz vor naheliegenden Fehlklassifikationen.
