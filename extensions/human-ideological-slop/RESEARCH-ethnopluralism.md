# RESEARCH: Ethnopluralismus als ideologische Strategie (LEX-2026-008, #94)

> Vollanalyse zum Lexikon-Eintrag `lexikon/entries/ethnopluralism.yaml` (LEX-2026-008).
> Eigenformulierung nach Rueda 2021, Havertz 2023/25, Spektorowska 2003, bpb, Wikipedia (EN/DE);
> keine CC-BY-SA-Übernahme ganzer Absätze (adr/0005-Prinzip).

## 1. Genealogie

Die moderne Form des Ethnopluralismus wurde von Alain de Benoist und der
Nouvelle Droite / GRECE formuliert („droit à la différence“,
Ethno-Differentialismus). Vorläufer stehen im französischen
Neonationalismus der 1950/60er (Binet, Europe-Action); den Begriff
„Ethnopluralismus“ prägte Henning Eichberg 1973. Aktivierungsform ist die
Identitäre Bewegung; in Deutschland über Kubitschek/IBD in AfD-Nähe.

## 2. Inhaltliche Behauptung

Kulturen werden als gleichwertig *und* unverträglich behauptet: Koexistenz
im selben Territorium zerstöre „Differenz“, also seien getrennte,
möglichst homogene Räume die einzige operationale Policy. Benoist (2002)
rahmt den Schwund von „Biodiversität“ und „Völkervielfalt“ parallel —
ökologische Mimikry.

## 3. Strategischer Kern: Rebranding statt Verzicht

Kein Verzicht auf Exklusion, sondern deren Rebranding: vom biologistischen
zum kulturalistischen Rassismus („cultural turn in racism“, Rueda 2021).
Egalitäres, antitotalitäres, antiimperialistisches und ökologisches
Vokabular wird übernommen, um Exklusionsziele anschlussfähig zu halten
(Taguieff: Tarnung suprematistischer Gehalte hinter egalitärem Vokabular).

## 4. Ambiguity als Design

Havertz („Ethnopluralism and its ambiguities: racism with and without
race“, JPI 2025) zeigt an Benoist, Faye, Eichberg, Lichtmesz: Cultural Turn
ja — aber biologistische Restargumentation bleibt; die Doppelbödigkeit ist
Design, nicht Nebeneffekt. Kultur fungiert als Race-Synonym, sobald
Zugehörigkeit an Deszendenz gebunden wird (Malik 2023, thesenweise).

## 5. Metapolitik als Slop-Generator

„Gramsci von rechts“ (Spektorowska 2003): kulturelle Hegemonie vor
Staat. Der Begriff taugt deshalb als Slop-Generator — er produziert endlose
„Differenz“-Prosa ohne operationalisierbare Policy außer
Trennung/Remigration.

## 6. Detektions-Relevanz (Verbindlich)

**Der Detektor bewertet die Strategieform, nicht die Parteizugehörigkeit.**
Entscheidend ist die Schlussform — von „Differenz/Vielfalt" auf getrennte
Räume oder Remigration —, nicht das Wort „Ethnopluralismus“ und nicht, wer
es sagt. Detect-only named evidence via Pattern `EthnopluralistRebrand`
(#92), kein Score (adr/0008).

- **Positiv-Signal:** „Recht auf Differenz“ als Politikforderung;
  Diversitäts-Vokabular mit Segregations-Schluss; ökologische Mimikry
  (Biodiversität ↔ Völkervielfalt).
- **Hard-Negatives:** Ethnografie/Historiografie, die Differenz beschreibt,
  ohne Trennung zu fordern; Statistik mit Nenner/Zeitraum/Quelle;
  Migrationsforschung ohne Deszendenz-Bindung von Zugehörigkeit.

## Querverweise

- Lexikon: `lexikon/entries/ethnopluralism.yaml` (LEX-2026-008)
- Ontologie: `IdeologicalSlop` → Pattern `EthnopluralistRebrand`
  (`extensions/human-ideological-slop/human_ideological_slop.json`,
  `skills/ai-slop-detection/references/de_ideology_patterns.json`)
- ADR 0008 (Geltungsbereich), #89 (Epic), #92 (Option B), #93, #95–#97
  (Fallstudien)
