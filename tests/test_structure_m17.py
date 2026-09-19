"""Issue #76 Rest — M17: Briefartiger Aufbau in Artikel-Kontext
(letter_like_structure, detect-only, structure_metrics.py).

Konzept aus docs/de-coverage.md M17 (NEU klein): Betreff/Anrede/
Grussformel als vollstaendiger Briefrahmen in einem Dokument, das
Artikel-Marker traegt — E-Mail-Schablone statt passendem Genre.
Sprachagnostisch DE+EN (Formeln).

Signal-DoD: je 3 Positiv / 3 Negativ / 2 Grenz-Fixtures; Konfidenz 0.5,
detect-only, nie Score-wirksam.
"""

import os
import sys

SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

import structure_metrics as sm  # noqa: E402


# --- M17: Briefartiger Aufbau ----------------------------------------------

M17_POS1 = (
    "# Die Zukunft des Homeoffice\n\n"
    "Betreff: Homeoffice ist die Zukunft\n\n"
    "Sehr geehrte Damen und Herren,\n\n"
    "- Flexibilitaet ist der Schluessel\n"
    "- Pendeln gehoert der Vergangenheit an\n"
    "- Produktivitaet steigt nachweislich\n\n"
    "Zusammengefasst verbindet diese Liste alle genannten Punkte.\n\n"
    "Mit freundlichen Gruessen\n"
)

M17_POS2 = (
    "# Product Launch\n\n"
    "Subject: Our exciting new release\n\n"
    "Dear team,\n\n"
    "The new version ships with a redesigned dashboard, a faster search "
    "index and a refreshed onboarding flow that guides every single "
    "user through the first steps with care and attention to detail.\n\n"
    "Best regards,\n"
)

M17_POS3 = (
    "## Workshop-Rueckblick\n\n"
    "Betreff: Danke fuer Ihre Teilnahme\n\n"
    "Guten Tag,\n\n"
    "1. Begruessung durch die Moderation\n"
    "2. Impulsvortrag zu agilen Methoden\n"
    "3. Weltcafe mit drei Stationen\n\n"
    "Viele Gruesse\n"
)

# Echte, kurze E-Mail: Briefrahmen ohne Artikel-Kontext -> kein Fire
M17_NEG1 = (
    "Betreff: Terminnaechste Woche\n\n"
    "Hallo Stefan,\n\n"
    "Passt dir Dienstag 14 Uhr fuer das Review? Sonst schlage ich\n"
    "Donnerstag vormittag vor.\n\n"
    "Viele Gruesse\n"
    "Renate"
)

# Artikel mit nur ANREDE (Newsletter-Stil), kein Betreff, keine
# Grussformel-Zeile am Zeilenanfang -> kein Fire
M17_NEG2 = (
    "# Newsletter Juli\n\n"
    "Liebe Leserinnen und Leser,\n\n"
    "Diese Ausgabe beleuchtet drei Themen: die neue DSGVO-Frist, ein\n"
    "Interview mit unserer Datenschutzbeauftragten und einen Rueckblick\n"
    "auf die Konferenz im Juni mit vielen Zahlen und Zitaten.\n"
)

# Richtige E-Mail MIT Laenge: Lang, aber Artikel-Marker fehlen -> kein Fire
M17_NEG3 = (
    "Subject: Quarterly numbers\n\n"
    "Dear Mr Smith,\n\n"
    "please find attached the quarterly numbers for Q2 as discussed in "
    "our last call. Revenue is up twelve percent year over year, while "
    "churn stayed flat at three point two percent, driven mainly by the "
    "new enterprise tier. I would suggest a short call next week to "
    "walk through the details and align on the forecast for Q3 and Q4.\n\n"
    "Kind regards,\n"
    "Jane"
)

# Nur Betreff + Grussformel, keine Anrede-Zeile -> kein Fire (halbvoll)
M17_BOUND1 = (
    "# Blogeintrag\n\n"
    "Betreff: Notizen\n\n"
    "- Punkt eins mit etwas Text rund um das Thema\n"
    "- Punkt zwei mit einem weiteren Gedanken dazu\n\n"
    "Mit freundlichen Gruessen\n"
)

# Kompletter Rahmen, aber reale Kurznachricht (kein Artikel-Marker,
# < 80 Woerter) -> kein Fire
M17_BOUND2 = (
    "Betreff: Lunch\n\n"
    "Guten Tag,\n\n"
    "Ich bin um 12:30 im Hofcafe, wenn du mitkommst sag kurz Bescheid,\n"
    "ich reserviere sonst einen Platz fuer uns beide drinnen.\n\n"
    "Herzliche Gruesse"
)


class TestM17LetterLikeStructure:
    def test_pos1_german_list_article(self):
        f = sm.letter_like_structure(M17_POS1)
        assert f is not None and f["id"] == "LetterLikeStructure"
        assert f["confidence"] <= 0.55
        assert "keep_when" in f

    def test_pos2_english_article(self):
        assert sm.letter_like_structure(M17_POS2) is not None

    def test_pos3_numbered_workshop(self):
        assert sm.letter_like_structure(M17_POS3) is not None

    def test_neg1_real_short_email(self):
        assert sm.letter_like_structure(M17_NEG1) is None

    def test_neg2_newsletter_no_full_frame(self):
        assert sm.letter_like_structure(M17_NEG2) is None

    def test_neg3_long_real_email_no_article_markers(self):
        assert sm.letter_like_structure(M17_NEG3) is None

    def test_boundary1_missing_salutation(self):
        assert sm.letter_like_structure(M17_BOUND1) is None

    def test_boundary2_short_real_note(self):
        assert sm.letter_like_structure(M17_BOUND2) is None


class TestM17Wiring:
    def test_find_structure_findings_includes_m17(self):
        findings = sm.find_structure_findings(M17_POS1)
        ids = {f["id"] for f in findings}
        assert "LetterLikeStructure" in ids
        for f in findings:
            assert f["confidence"] <= 0.55
            assert "keep_when" in f
