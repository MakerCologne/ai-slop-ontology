"""FU-17: check_ssot deckt den de_*-Phrase-Layer ab (RI-4 aus Review I).

Bisher war Manipulation am de_*-Layer nur durch Suite-Tests sichtbar,
check_ssot blieb gruen (Manipulationsprobe B im Review). Neue Pruefung C4:

  - jeder de_*-Kategorie in ontology.json muss im DE_LAYER-Pin stehen
    (Kategorie + Item-Anzahl + Evidence-Regel: jede Phrase >= 1 Beleg,
    Wikipedia-Quellen nur mit Namespace-Praefix /wiki/Wikipedia:...)
  - gepinnte Kategorien muessen noch existieren (Stichprobe gegen
    Loeschen von Kategorien)
  - Manipulation (Evidence entfernt, Phrase hinzugefuegt, Kategorie
    umbenannt) laesst check_ssot mit Exit 1 fehlschlagen (Probe hier
    als Test gefahren, dokumentiert in burn-batch-j.md)
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECK = os.path.join(ROOT, "scripts", "check_ssot.py")
ONTOLOGY = os.path.join(ROOT, "ontology.json")


def _run_check(workdir: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, os.path.relpath(CHECK, workdir)],
        cwd=workdir, capture_output=True, text=True)


class DeLayerPin(unittest.TestCase):
    def test_check_green_on_clean_repo(self):
        r = _run_check(ROOT)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("de_*-Phrase-Layer", r.stdout)

    def test_pin_covers_all_de_categories(self):
        with open(ONTOLOGY, encoding="utf-8") as f:
            cats = json.load(f)["signals"]["text"]["phrases"]["categories"]
        de_cats = sorted(c for c in cats if c.startswith("de_"))
        self.assertTrue(de_cats)
        # Pin-Struktur via Modulimport pruefen
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import check_ssot  # noqa: E402
        pinned = sorted(check_ssot.DE_LAYER)
        self.assertEqual(de_cats, pinned,
                         "Pin und ontology.json weichen ab")

    def _tamper(self, mutate) -> subprocess.CompletedProcess:
        import shutil
        with tempfile.TemporaryDirectory() as td:
            for rel in ("scripts", "src", "ontology.json",
                        "skills"):
                src = os.path.join(ROOT, rel)
                dst = os.path.join(td, rel)
                if os.path.isfile(src):
                    shutil.copy(src, dst)
                else:
                    shutil.copytree(src, dst,
                                    ignore=shutil.ignore_patterns(
                                        "__pycache__"))
            # references/ontology.json ist ein Symlink -> neu verlinken
            reflink = os.path.join(td, "skills", "ai-slop-detection",
                                   "references", "ontology.json")
            if os.path.islink(reflink):
                os.remove(reflink)
                os.symlink("../../../ontology.json", reflink)
            mutate(td)
            return _run_check(td)

    def test_probe_removed_evidence_fails(self):
        def mutate(td):
            p = os.path.join(td, "ontology.json")
            o = json.load(open(p, encoding="utf-8"))
            ev = o["signals"]["text"]["phrases"]["categories"][
                "de_transitions"]["evidence"]
            ev.pop("ferner")
            json.dump(o, open(p, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=2)
        r = self._tamper(mutate)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("de_transitions", r.stdout)

    def test_probe_added_unpinned_de_category_fails(self):
        def mutate(td):
            p = os.path.join(td, "ontology.json")
            o = json.load(open(p, encoding="utf-8"))
            o["signals"]["text"]["phrases"]["categories"][
                "de_sneaky"] = {
                    "confidence": 0.6, "items": ["x y z"],
                    "evidence": {"x y z": [
                        {"source": "own:probe", "note": "x"}]}}
            json.dump(o, open(p, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=2)
        r = self._tamper(mutate)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("de_sneaky", r.stdout)

    def test_probe_removed_de_category_fails(self):
        def mutate(td):
            p = os.path.join(td, "ontology.json")
            o = json.load(open(p, encoding="utf-8"))
            del o["signals"]["text"]["phrases"]["categories"]["de_recap"]
            json.dump(o, open(p, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=2)
        r = self._tamper(mutate)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("de_recap", r.stdout)

    def test_probe_bare_wikipedia_url_without_namespace_fails(self):
        def mutate(td):
            p = os.path.join(td, "ontology.json")
            o = json.load(open(p, encoding="utf-8"))
            srcs = o["signals"]["text"]["phrases"]["categories"][
                "de_transitions"]["evidence"]["ferner"]
            srcs[0]["source"] = (
                "https://de.wikipedia.org/wiki/Anzeichen_für_"
                "KI-generierte_Inhalte")
            json.dump(o, open(p, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=2)
        r = self._tamper(mutate)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("Namespace", r.stdout)


if __name__ == "__main__":
    unittest.main()
