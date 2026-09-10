"""Tests for model_notes / signalModelDynamics (issue #36).

Validates the SSOT section in ontology.json: schema, evidence rule,
per-signal model_notes presence, and half-life vocabulary.
"""

import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONTOLOGY = os.path.join(ROOT, "ontology.json")

with open(ONTOLOGY, encoding="utf-8") as f:
    ONT = json.load(f)

SMD = ONT.get("signalModelDynamics", {})
VALID_HALF_LIFE_PREFIXES = ("short", "medium", "long", "unmeasured")


class TestSignalModelDynamics(unittest.TestCase):
    def test_section_exists_with_source(self):
        self.assertIn("version", SMD)
        self.assertIn("lastUpdated", SMD)
        self.assertIn("#36", SMD.get("source", ""))
        for key in ("scope", "evidence", "review"):
            self.assertIn(key, SMD.get("rules", {}), f"missing rule: {key}")

    def test_half_life_guidance_categories(self):
        cats = SMD.get("halfLifeGuidance", {}).get("categories", {})
        for cat in ("short", "medium", "long"):
            self.assertIn(cat, cats)

    def test_entries_have_required_fields_and_evidence(self):
        entries = SMD.get("entries", {})
        self.assertGreaterEqual(len(entries), 4, "expected at least 4 documented entries")
        for signal, entry in entries.items():
            self.assertIn("model_notes", entry, signal)
            self.assertTrue(entry["model_notes"].strip(), signal)
            self.assertIn("half_life", entry, signal)
            self.assertIn("evidence", entry, signal)
            self.assertTrue(entry["evidence"].strip(), f"{signal}: evidence required (M6)")
            prefix_ok = any(entry["half_life"].startswith(p) for p in VALID_HALF_LIFE_PREFIXES)
            self.assertTrue(prefix_ok, f"{signal}: invalid half_life {entry['half_life']!r}")

    def test_entries_reference_real_signals(self):
        """Every documented entry must map to a signal id/name in the ontology."""
        known = set()

        def walk(obj):
            if isinstance(obj, dict):
                if "id" in obj:
                    known.add(obj["id"])
                for k, v in obj.items():
                    known.add(k)
                    walk(v)
            elif isinstance(obj, list):
                for v in obj:
                    walk(v)

        walk(ONT)
        for signal in SMD.get("entries", {}):
            self.assertIn(signal, known, f"entry {signal} has no signal in ontology.json")

    def test_per_signal_model_notes_present(self):
        """Pilot signals carry inline model_notes where the issue names them."""
        ids_with_notes = set()

        def collect(obj):
            if isinstance(obj, dict):
                if "id" in obj and "model_notes" in obj:
                    ids_with_notes.add(obj["id"])
                if "model_notes" in obj and "id" not in obj:
                    pass
                for v in obj.values():
                    collect(v)
            elif isinstance(obj, list):
                for v in obj:
                    collect(v)

        collect(ONT)
        for expected in ("ExcessiveEmDash", "EmDashExcess", "CurlyQuotes"):
            self.assertIn(expected, ids_with_notes)

        # ImportancePuffery is keyed by name, not id
        def find_key(obj, key):
            if isinstance(obj, dict):
                if key in obj and isinstance(obj[key], dict) and "model_notes" in obj[key]:
                    return True
                return any(find_key(v, key) for v in obj.values())
            if isinstance(obj, list):
                return any(find_key(v, key) for v in obj)
            return False

        self.assertTrue(find_key(ONT, "ImportancePuffery"))

    def test_loop_guard_doc_exists(self):
        doc = os.path.join(ROOT, "docs", "loop-guards", "36-model-dynamics.md")
        self.assertTrue(os.path.isfile(doc))


if __name__ == "__main__":
    unittest.main()
