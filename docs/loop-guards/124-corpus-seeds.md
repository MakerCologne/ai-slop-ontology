# Loop-Guard #124 — Labeled-Corpus Seeds (BS-I2)

Status: **Seed-Register etabliert, Download/Ingestion offen** · Issue [#124](https://github.com/MakerCologne/ai-slop-ontology/issues/124) · 2026-09-12

## Zweck

Startpunkt für den gelabelten Korpus (BS-I2): Kuratiertes Register der Datensatz-Kandidaten aus `meow-d/slop-alerter` `ml/`-Ordner (Kaggle/HF), bevor irgendetwas heruntergeladen wird. Maschinenlesbar: [`eval/dataset_seeds.json`](../../eval/dataset_seeds.json) (Schema v1, `test_data_files.py` validiert Struktur).

## Warum ein Register statt sofortigem Download

1. **Lizenz-First:** Ein Kandidat (linkedin_posts) hat keine deklarierte Lizenz → selection rule 3 sperrt ihn aus, bis geklärt.
2. **Provenance-First:** AI-Label ohne Modell-/Pipeline-Nachweis ist unbrauchbar (sonst lernt der Detektor "modernes Schreiben", nicht "Slop").
3. **Genre-Schutz:** Kein Kandidat deckt dieGenres ab, die unsere Hard-Negatives brauchen (GitHub/academic) — das bleibt Handarbeit.

## Auswahlregeln (verbindlich, in JSON manifest)

1. AI-Label braucht Modell-Provenance oder verifizierbare Generierungs-Pipeline.
2. Human-Label braucht Pre-LLM-Cutoff (< 2022-11) oder verifizierte menschliche Herkunft.
3. Keine Lizenz → kein Eintritt in den Korpus.
4. Max. 25% des Endkorpus pro Quelle (Single-Source-Style-Bias).
5. Dedup per sha1(normalisierter Text) vor Split; Cross-Dataset-Dedup Pflicht (Reddit/Twitter-Spiegel).

## Priorisierung

- **Hoch:** raid (nach Adversarial-Ausschluss), aigtbench, reddit_ds_posts
- **Mittel:** claude_fable (nur im Mix), unmasking, moltbook, sentiment140, linkedin_influencers (Hard-Negative für EngagementSlop!)
- **Niedrig:** lmsys_chat_gpt5 (Chat-Register), reddit_1m_comments (Datum ungeprüft), linkedin_posts (Lizenz offen)

## Bekannte Lücken (bewusst dokumentiert)

- GitHub/academic Hard-Negatives: nirgendwo im Topic verfügbar, selbst slop-alerter ungelöst → Handbau.
- DE: alle Kandidaten EN → DE-Korpus bleibt handcrafted.
- ZH/JA (A9/A10): leer im gesamten Topic — bestätigt unsere Vorsprungsthese.

## Nächste Schritte (abgeleitet, offene DoD-Punkte)

1. RAID-Lizenz klären (raid-bench.xyz), dann Probenziehung + Ingestion-Skript (adaptiertes preprocess.py, das slop-alerter-Pattern folgt: pro Quelle ein `extract_*()`, sha1-Dedup, `{text,label}`-jsonl).
2. Sammlungsdaten der Kaggle-Kandidaten verifizieren (reddit_1m_comments, linkedin_influencers) gegen Cutoff-Regel.
3. Genre-Hard-Negatives GitHub/academic handgebaut (separates Issue).

## Quellen

- meow-d/slop-alerter `ml/data/download.py` + `preprocess.py` (Datensatzliste + Extraktions-Pattern)
- HF-API Lizenz-Check 2026-09-12: claude_fable=MIT, aigtbench=Apache-2.0, unmasking=CC-BY-4.0, lmsys=CC-BY-4.0, moltbook=MIT, linkedin_posts=keine
