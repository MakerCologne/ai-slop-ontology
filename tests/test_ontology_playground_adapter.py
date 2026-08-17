import subprocess
import sys
import unittest
from pathlib import Path


class OntologyPlaygroundAdapterTests(unittest.TestCase):
    def test_adapter_structure_and_manifest(self):
        root = Path(__file__).resolve().parents[1]
        validator = root / "integrations" / "ontology-playground" / "validate_adapter.py"
        result = subprocess.run(
            [sys.executable, str(validator)],
            cwd=root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("7 catalogue entries", result.stdout)


if __name__ == "__main__":
    unittest.main()
