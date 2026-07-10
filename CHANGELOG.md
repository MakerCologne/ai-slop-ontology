# Changelog

## [1.1.0] — 2026-07-10

### Recherche & Ontologie
- **Neue Slop-Typen** (forschungsbelegt):
  - `SecurityReportSlop` — KI-generierte Schwachstellen-Reports; curl beendete sein
    HackerOne-Bug-Bounty im Februar 2026 (~20 % Slop-Anteil, Confirmed-Rate <5 %).
  - `PeerReviewSlop` — KI-generierte Peer-Reviews; Organization Science (2026):
    >30 % der Reviews KI-beteiligt, Feedback wird enger und weniger substanziell.
- **Neues Image-Signal** `HyperTypicality`: KI-Gesichter wirken „typischer als echte"
  (Regression zum mathematischen Mittel); Menschen sind darauf trainierbar
  (ANU/PNAS 2026, near-perfect Accuracy).
- **Schlüsselzahlen aktualisiert** (Stand Juli 2026): NewsGuard 3.749 Content-Farmen
  (23.06.2026); Deezer 44 % AI-Anteil an Neu-Uploads (~75.000 Tracks/Tag, nur 1–3 %
  der Streams, ~85 % davon Fraud); Spotify 75 Mio.+ entfernte Spam-Tracks;
  Organization Science +42 % Submissions seit ChatGPT.
- **8 neue Referenzen** (REFERENCES.md #31–38), darunter die Gegenposition
  Nishal/Sax/Kieslich (arXiv:2606.12285) zu Kommers et al.
- **Alle Kernzitate verifiziert**: Shaib et al. (arXiv:2509.19163), Madsen & Puyt
  (SSRN 5558018), Kommers et al. (arXiv:2601.06060), Keisha et al. (arXiv:2509.04796).
- Kanonisches Dokument umbenannt: `AI-SLOP-ONTOLOGY-v1.0.0.md` → `AI-SLOP-ONTOLOGY.md`
  (Version steht im Front Matter).

### Detection-Engine (Bugfixes aus dem Deep Review, siehe REVIEW-2026-07.md)
- **Word-Boundary-Matching**: Buzzwords matchen keine Teilwörter mehr
  („dynamic" ≠ „thermodynamics").
- **Overlap-Deduplizierung**: Überlappende Begriffe zählen einmal, längster Match
  gewinnt („rich tapestry" schluckt „tapestry").
- **Multilingual-Fix** (Skill-Scorer): Groß-/kleinschreibungs-Bug behoben — deutsche
  Marker wie „im digitalen Zeitalter" wurden nie erkannt (Vergleich von
  Original-Casing gegen lowercase-Text).
- **Burstiness-Neutralität**: Texte mit <3 Sätzen werden nicht mehr fälschlich als
  „uniform" (= AI-artig) gewertet.
- **Severity-gewichtetes Scoring** (`src/classifier.py`): Die dokumentierte Formel
  `min(1, Σ w(severity)·confidence / n)` mit Eskalation (critical ∨ ≥2 high → ≥0,70)
  ist jetzt tatsächlich implementiert; vorher wurde nur der Confidence-Mittelwert
  gebildet und das `weights`-Dict war toter Code.
- **Multilingual-Floor**: ≥3 multilinguale AI-Marker heben den Score auf mindestens
  0,40 („Suspicious"), da englisch-basierte Dimensionen nicht-englische Texte verwässern.
- **Mirrored-Intro/Conclusion**: Stopword-Filterung reduziert False Positives.
- `get_signal_stats()` listet „description" nicht mehr als Sprache.
- SKILL.md: falscher relativer Pfad zur Ontologie korrigiert; 14 statt 12 Slop-Typen.

### Infrastruktur
- Testsuite unter `tests/` (stdlib `unittest`, keine Zusatz-Dependencies).
- `LICENSE` (CC BY 4.0) ergänzt — README versprach die Lizenz bereits.
- GitHub-Actions-Workflow für Tests.

## [1.0.0] — 2026-05-20

- Initial Release: kanonisches Dokument, YAML/JSON/TTL-Ontologie, Klassifikator,
  Scorer, Skill `ai-slop-detection`, 459 Signale, 22 Detection-Techniken,
  12 Harm-Klassen.
