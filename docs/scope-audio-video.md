# Scope Audio & Video — 4./5. Median-Klasse (Issue #44)

**Status:** Scope-Doku (kartiert, nicht implementiert) · **Datum:** 2026-09-06
**Bezug:** Issue #44 · Backlog btm-openclaw-platform #1129 · Gap-Report `report-extended.md` Abschnitt 1, Blind-Spots BS-I*
**Muster:** analog zur Bild-Ausgrenzung (SKILL.md verweist Bildanalyse an den `image`-Tool); #15 (UI-Slop) zeigt das Muster Medien-Klassen.
**Lizenz-Hinweis:** Alle Signal-Namen und Beschreibungen sind eigene Formulierungen; keine Übernahme aus Fremdquellen.

## Geltungsbereich

Audio- und Video-Slop sind ab hier **kartierte Klassen mit definiertem Erkennungsweg**, aber kein Bestandteil der deterministischen Text-Engine. Die Engine (`src/`) bewertet weiterhin Text, Code und webnahes Markup; Medien-Container (`.mp3`, `.mp4`, `.wav`, …) und Medien-Streams werden nicht geöffnet und nicht gescannt.

Die Trennung folgt ADR-0006 (detect-only, kein Rewriter) und der Verifikationsleiter (`docs/metric/VERIFICATION-LADDER.md`): Ein Signal zählt nur dann als deterministisch, wenn es ohne Modell-Beteiligung maschinell prüfbar ist. Alles andere läuft über den Tool-Prompt des Agenten (LLM als fakultativer Zweitscanner, vgl. #57) und trägt per Definition keine Gate-Verbindlichkeit.

## Audio-Slop: Signal-Katalog (≥10)

Legende der Erkennungswege: **D** = deterministisch (parsbar, maschinell, kein Modell), **P** = nur via Tool-Prompt (Modell-Beobachtung, nicht gate-fähig).

| # | Signal | Weg | Prüfvorschrift |
|---|---|---|---|
| A1 | C2PA/Content-Credentials-Manifest in Audiodatei | D | Manifest-Parsing (c2pa.org-Spezifikation); Abwesenheit ist kein Negativbeweis |
| A2 | Provenance-Marker von TTS-Anbietern (z.B. ElevenLabs-Metadaten, Wasserzeichen wie AudioSeal/SynthID-Audio) | D | Vendor-Detektoren bzw. Marker-Dekodierung; nur positive Befunde zählen |
| A3 | Speaker-Etikett / Stimmen-ID in Container-Metadaten (synthetische Sprecher-Kennung) | D | Tag-Inspektion in ID3/MP4-Atom-Struktur |
| A4 | Generierungs-Pipeline-Metadaten (Tool-Name, Modell-Version, Zeitstempel im Container) | D | Metadaten-Felder gegen Liste bekannter Generatoren prüfen |
| A5 | Gesprächspausen-Statistik unnatürlich gleichförmig (keine Überlappungen, Pausen quantisiert) | P | Modell beurteilt Transkript-Timing; kein deterministischer Cut-off |
| A6 | Intonations-Uniformität über lange Passagen (flache Pitch-Varianz, fehlende Sprechnervosität) | P | Modell-Beobachtung, akustische Merkmalsprüfung außerhalb des Scopes |
| A7 | Default-Stil-Cluster generierter Musik ("ambient lo-fi", "epic cinematic trailer") als Titel/Tag-Muster | D | String-Match auf Phrasen-Katalog in Metadaten/Titeln (analog Buzzword-Tiers) |
| A8 | Loop-Längen-Quantisierung in generierter Musik (exakte Takt-Wiederholung, Bit-identische Segmente) | D | Korrelations-Analyse auf PCM-Ebene (technisch möglich, aber nicht Teil der Text-Engine → Tool-Auftrag) |
| A9 | Transkript trägt Text-Slop-Signale (SSOT-Engine-Score auf ASR-Ausgabe) | D | bestehende Engine auf Transkript; Deckelung durch Genre-Opt-in ADR-0004 |
| A10 | Cross-Modal-Mismatch: Audio-Inhalt widerspricht Metadaten/Beschreibung | P | Modell vergleicht Transkript gegen Container-Metadaten |
| A11 | Sprecherwechsel-Rhythmus artifiziell regelmäßig (feste Wechselintervalle, Podcast-"Dialog"-Default) | P | Modell-Beobachtung |
| A12 | Fehlen jeder Produktionsartefakte (kein Raumrauschen, kein Atemgeräusch über lange Dauer) | P | Modell-Beobachtung; kein Schwellwert-Test definiert |

## Video-Slop: Signal-Katalog (≥10)

| # | Signal | Weg | Prüfvorschrift |
|---|---|---|---|
| V1 | C2PA-Manifest / Content Credentials in Videodatei | D | wie A1 |
| V2 | Provider-Wasserzeichen-Frame (SynthID Pixel-Marker, Visible-Watermark-Overlay) | D | Vendor-Detektor bzw. Bildbereichs-Analyse |
| V3 | Generierungs-Metadaten im Container (Encoder-Signatur bekannter Video-Generatoren, Runway/Veo/Sora-typische Tags) | D | Metadaten-Inspektion gegen Generator-Liste |
| V4 | Untertitel-/Transkript-Spur trägt Text-Slop (Engine-Score auf Caption-Track) | D | bestehende Engine; stärkstes deterministisches Quersignal |
| V5 | Shorts-Struktur-Default in Metadaten/Kapitelmarken: Hook → N Punkte → CTA als starre Kapitel-Taktung | D | Kapitel-/Timestamp-Muster-Match; Text-Spur zusätzlich per Engine (typePatterns-Analogon) |
| V6 | KI-Nachrichtensprecher-Artefakte (Avatar-Blinzel-Rhythmus, Mund-Sync-Drift) | P | Modell-Beobachtung; keine deterministische Messvorschrift |
| V7 | B-Roll-Default-Wiederverwendung: identische Sequenz-Segmente über mehrere Clips desselben Kanals | D | Perceptual-Hash-Vergleich (technisch, als Tool-Auftrag; kein Engine-Bestandteil) |
| V8 | Physik-Unmöglichkeiten in Bewegung (Objekt-Morphing, Bein-Phasen-Sprünge) | P | Modell-Beobachtung, analog Bild-Signal 14 |
| V9 | Text-in-Video-Overlay trägt Engine-Slop-Signale (OCR der Overlay-Ebenen, Score wie V4) | D | OCR + bestehende Engine |
| V10 | Audio-Video-Sync-Drift typisch für generierte Stimmen-Tracks (Lippensync-Offset konstant, nicht driftend) | P | Modell-Beobachtung |
| V11 | Thumbnail/Titel trägt Text-Slop (Engine-Score auf Titel + OCR des Thumbnails) | D | bestehende Engine |
| V12 | Cross-Modal-Mismatch: Caption-Track widerspricht Bildinhalt systematisch | P | Modell-Beobachtung (Signal 15 der Ontologie angewandt auf Video) |

## Was die Engine heute schon kann

Zwei der deterministischen Signale sind ohne Medien-Parsing verfügbar, weil sie an Textspuren andocken: `A9` und `V4`/`V5`/`V9`/`V11` laufen auf beliebigen Texteingaben (Transkripte, Caption-Dateien, Titel), die der Aufrufer liefert. Der Agent darf Medieninhalte also **nach dieser Vorschrift** indirekt scorieren: Erst transkribieren/OCR-en, dann die Textspur durch die Engine geben, Ergebnis als Text-Slop-Score der Spur ausweisen — nie als "Video ist KI-generiert".

## Was außerhalb des Scopes bleibt

- Akustische Forensik (Pitch-Statistik, Spektralanalyse) und visuelle Frame-Analyse: kein Bestandteil der Ontologie-Engine, kein Gate.
- Negative Beweise ("kein C2PA-Manifest vorhanden, also KI") sind ausdrücklich unzulässig; Provenanz-Signale sind nur in positiver Richtung verwertbar.
- Stimmen-Klonsuche an Einzelpersonen (Speaker-Identification) ist Detektions- wie auch missbrauchsrelevant und bleibt bewusst unspezifiziert.

## DoD-Abgleich (Issue #44)

- [x] Scope-Dokument mit ≥10 konkreten Signalen je Medium (A1–A12, V1–V12)
- [x] Trennung deterministisch vs. Tool-Prompt je Signal
- [x] Scope-Statement in `SKILL.md` (analog Bild-Ausgrenzung), Rückverweis auf dieses Dokument
- [ ] TTS-Provenance-Implementierung (Vendor-Detektoren für A2) — bewusst außerhalb dieses Issues, Folgearbeit
