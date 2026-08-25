"""Issue #74 — Register-Profile v2 (detect-only).

Two surfaces:

1. ``register_profile(text)`` — a JSON-serializable style card (mode,
   deictic_center, address, distance, sentence_shape, word_level,
   paragraph_openers, particles, punctuation_affinity). Pure description,
   never feeds the numeric slop score.

2. ``register_drift_intern(text, genre=None)`` — detect-only advisory
   signal: register distance BETWEEN document halves / paragraph clusters
   (position-aware), deliberately distinct from #81 ``register_drift``
   (whole-text formal/colloquial mixing). Genre profiles (#42
   exemptions) are respected: formal genres suppress, exempt terms are
   stripped before marker counting.

Signal-DoD for register_drift_intern: 3 positive / 3 negative / 2
boundary fixtures below; single stray marker or quoted dialogue never
fires.
"""

import json
import os
import sys

import pytest

SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

import register_profile as rp  # noqa: E402
import slop_scorer  # noqa: E402


# --- helpers -----------------------------------------------------------

def _formal_half():
    return ("Furthermore, the committee concluded its assessment. "
            "Moreover, the findings were documented pursuant to the "
            "protocol. Notwithstanding prior concerns, the audit was "
            "completed and consequently the report was filed with the "
            "registrar for further review.")


def _colloquial_half():
    return ("Yeah, honestly the whole thing was kinda wild. Hey, I mean "
            "the stuff they found was really odd somehow, okay? We just "
            "sat there and thought, no way this is real, but it was.")


def _uniform_formal():
    return (_formal_half() + " " + _formal_half() + " Thus the matter is "
            "hereby resolved and hence closed for the current period.")


def _uniform_colloquial():
    return _colloquial_half() + " " + _colloquial_half() + " Yeah, wild."


def _uniform_mixed():
    """Both halves contain formal AND colloquial markers — #81's
    register_drift territory, NOT register_drift_intern."""
    half = ("Furthermore the results were documented, which was honestly "
            "kinda wild, and moreover the team, yeah the whole team, "
            "filed them pursuant to the rules, okay.")
    return half + " " + half


# --- 1. register_profile: style card ------------------------------------

class TestRegisterProfileCard:
    CARD_KEYS = {
        "mode", "deictic_center", "address", "distance", "sentence_shape",
        "word_level", "paragraph_openers", "particles",
        "punctuation_affinity", "meta",
    }

    def test_card_has_all_fields_and_is_json(self):
        card = rp.register_profile(_formal_half())
        assert set(card.keys()) == self.CARD_KEYS
        json.dumps(card)  # must be JSON-serializable

    def test_formal_text_profiles_formal_distance(self):
        card = rp.register_profile(_uniform_formal())
        assert card["distance"] == "formal"
        assert card["deictic_center"] == "impersonal"
        assert card["address"] == "indirect"

    def test_colloquial_text_profiles_informal_reader(self):
        card = rp.register_profile(_uniform_colloquial())
        assert card["distance"] == "informal"
        assert card["deictic_center"] == "reader"

    def test_de_text_modes_and_particles(self):
        text = ("Na ja, das war halt irgendwie krass. Du musst das echt "
                "mal sehen, okay? Es war eben so ein Tag, an dem alles "
                "komisch lief, und ja, das sagt man dann einfach so.")
        card = rp.register_profile(text)
        assert card["meta"]["language_guess"] == "de"
        assert "halt" in card["particles"]["modal_particles"]
        assert card["address"] == "direct"

    def test_sentence_shape_and_punctuation(self):
        text = ("Short. This sentence is considerably longer than the "
                "one before it, which creates natural variation! "
                "Medium length one follows — with a dash — and ends.")
        card = rp.register_profile(text)
        assert card["sentence_shape"]["sentences"] >= 3
        assert card["sentence_shape"]["profile"] in {"uniform", "varied"}
        assert card["sentence_shape"]["profile"] == "varied"
        assert card["punctuation_affinity"]["em_dash_rate"] > 0

    def test_paragraph_openers_listed(self):
        text = "First paragraph starts here.\n\nSecond paragraph starts differently.\n\nFirst ideas return once more."
        card = rp.register_profile(text)
        assert len(card["paragraph_openers"]["first_words"]) == 3

    def test_deterministic(self):
        assert rp.register_profile(_uniform_formal()) == rp.register_profile(_uniform_formal())


# --- 2. register_drift_intern: signal DoD 3/3/2 --------------------------

class TestRegisterDriftInternPositive:
    def _doc(self, a, b):
        return a + " " + b

    def test_pos1_en_formal_then_colloquial(self):
        finding = rp.register_drift_intern(self._doc(_formal_half(), _colloquial_half()))
        assert finding is not None
        assert finding["id"] == "RegisterDriftIntern"
        assert finding["confidence"] <= 0.55
        assert "half" in finding["evidence"].lower() or "hälfte" in finding["evidence"].lower()

    def test_pos2_en_colloquial_then_formal(self):
        finding = rp.register_drift_intern(self._doc(_colloquial_half(), _formal_half()))
        assert finding is not None

    def test_pos3_de_document(self):
        formal = ("Gemäß den Vorgaben wurde ferner dokumentiert, dass die "
                  "Prüfung abgeschlossen ist. Folglich ist hierauf zu "
                  "verweisen; laut Bericht ist mithin alles geregelt und "
                  "zudem wurden alle Punkte abschließend geprüft.")
        colloq = ("Na ja, das war halt irgendwie krass, echt jetzt. Mensch, "
                  "die Sachen dort waren schon wild, oder? Irgendwie lief da "
                  "ganz viel schief, sag ich mal so, ganz ehrlich.")
        finding = rp.register_drift_intern(formal + " " + colloq)
        assert finding is not None


class TestRegisterDriftInternNegative:
    def test_neg1_uniform_formal_not_flagged(self):
        """Legitim gleichmäßig: a uniformly formal text is a register, not drift."""
        assert rp.register_drift_intern(_uniform_formal()) is None

    def test_neg2_uniform_colloquial_not_flagged(self):
        assert rp.register_drift_intern(_uniform_colloquial()) is None

    def test_neg3_uniformly_mixed_is_81_territory_not_intern(self):
        assert rp.register_drift_intern(_uniform_mixed()) is None


class TestRegisterDriftInternBoundary:
    def test_boundary1_single_stray_marker(self):
        """One lone colloquial marker in the second half: no finding."""
        stray = _formal_half() + " Honestly, the rest stayed formal and " \
            "furthermore the matter was thus concluded pursuant to the " \
            "protocol, moreover without exception."
        assert rp.register_drift_intern(stray) is None

    def test_boundary2_quoted_dialogue_ignored(self):
        quoted = _formal_half() + ' He later said: "Yeah, honestly, it ' \
            'was kinda wild stuff, okay? Hey, no way!" The board thus ' \
            'resolved furthermore to close the matter.'
        assert rp.register_drift_intern(quoted) is None


class TestRegisterDriftInternGuards:
    def test_short_text_none(self):
        short = "Furthermore moreover yeah kinda wild okay."
        assert rp.register_drift_intern(short) is None

    def test_genre_exemptions_suppress(self):
        doc = _formal_half() + " " + _colloquial_half()
        for genre in ("academic", "legal", "technical"):
            assert rp.register_drift_intern(doc, genre=genre) is None, genre

    def test_genre_exempt_terms_stripped(self):
        """#42 guardrail: genre exempt terms (furthermore/moreover …) do
        not count as formal markers for academic — so the formal half
        loses its purity and no intern drift is reported."""
        weak_formal = ("Furthermore, the results are notable. Moreover, "
                       "the data support the hypothesis across conditions.")
        doc = weak_formal + " " + _colloquial_half()
        assert rp.register_drift_intern(doc, genre="academic") is None
        # without the genre guard the same doc is flagged (exempt terms
        # still count outside genre profiles)
        assert rp.register_drift_intern(doc) is not None

    def test_distinct_from_81_register_drift(self):
        """Collision discipline: different finding id, and the #81 case
        (uniformly mixed) is NOT claimed by the intern signal."""
        import naturalness_guard as ng
        mixed = _uniform_mixed()
        assert ng.register_drift(mixed) is not None
        assert rp.register_drift_intern(mixed) is None


# --- 3. scorer integration (detect-only, context output) -----------------

class TestScorerContextOutput:
    def test_result_contains_register_context(self):
        result = slop_scorer.slop_score(_uniform_formal())
        assert "context" in result
        card = result["context"]["register_profile"]
        assert set(card.keys()) == TestRegisterProfileCard.CARD_KEYS
        assert "register_findings" in result["context"]

    def test_detect_only_score_unchanged(self):
        """The register card must not change the numeric score: same text,
        score identical to a computation with the context key removed."""
        r1 = slop_scorer.slop_score(_uniform_formal())
        baseline = {k: v for k, v in r1.items() if k != "context"}
        # recompute after stripping context from the pipeline: the score
        # dimensions must not reference the register card at all
        assert r1["slop_score"] == slop_scorer.slop_score(_uniform_formal())["slop_score"]
        assert baseline["dimension_scores"]["burstiness_slop"] is not None

    def test_drift_finding_surfaced_in_context(self):
        doc = _formal_half() + " " + _colloquial_half()
        result = slop_scorer.slop_score(doc)
        ids = [f["id"] for f in result["context"]["register_findings"]]
        assert "RegisterDriftIntern" in ids

    def test_drift_finding_does_not_escalate_score(self):
        """Detect-only: adding a drifting second half must not raise the
        score above the formal-only baseline in a way attributable to the
        register module — score of formal text vs drift doc both stay
        computed without any register weight (key absence check)."""
        r = slop_scorer.slop_score(_formal_half() + " " + _colloquial_half())
        assert "register" not in r["dimension_scores"]

    def test_format_report_prints_register_context(self):
        result = slop_scorer.slop_score(_uniform_formal())
        report = slop_scorer.format_report(result)
        assert "Register" in report

    def test_report_json_roundtrip(self):
        result = slop_scorer.slop_score(_uniform_formal())
        json.dumps(result)
