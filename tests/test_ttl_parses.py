"""The Turtle serialization must parse — guards against undeclared prefixes.

Regression: ontology.ttl used the `xsd:` prefix without declaring it, so every
RDF tool failed to load it. This test parses the file when rdflib is available
(and is a no-op skip otherwise, so the stdlib-only test run stays green).
"""

import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TTL = os.path.join(ROOT, "ontology.ttl")

try:
    import rdflib
    HAVE_RDFLIB = True
except ImportError:
    HAVE_RDFLIB = False


class TurtleParsesTests(unittest.TestCase):
    @unittest.skipUnless(HAVE_RDFLIB, "rdflib not installed")
    def test_ontology_ttl_parses(self):
        g = rdflib.Graph()
        g.parse(TTL, format="turtle")
        self.assertGreater(len(g), 0)

    def test_xsd_prefix_is_declared_if_used(self):
        # Prefix-declaration check runs even without rdflib.
        with open(TTL, encoding="utf-8") as f:
            ttl = f.read()
        if "xsd:" in ttl:
            self.assertIn("@prefix xsd:", ttl,
                          "ontology.ttl uses xsd: but never declares the prefix")


if __name__ == "__main__":
    unittest.main()
