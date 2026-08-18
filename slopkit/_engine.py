"""Engine adapter: load the canonical detectors and expose one composed API.

Reuses (never re-implements):
  - src/classifier.py            → SlopClassifier (text + code, reads ontology.json)
  - skills/.../rhetorical_patterns → find_rhetorical_patterns (detect-only)

Those live outside the `slopkit` package in the repository, so they are
force-included into the wheel as `slopkit.engine` and `slopkit.skill` (see
pyproject.toml). Both layouts are supported here:

  installed wheel   → import slopkit.engine.classifier
  checkout/editable → add <repo>/src and the skill script dir to sys.path

Before this, the modules were only ever found by filesystem path, so an
installed `slop` crashed on every subcommand (review 2026-08 §1.1).
"""

import os
import sys
from functools import lru_cache
from pathlib import Path


def repo_root() -> Path:
    """Repository root, or the package parent when installed as a wheel.

    Overridable with SLOP_REPO_ROOT for unusual layouts.
    """
    env = os.environ.get("SLOP_REPO_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parent.parent


def in_checkout() -> bool:
    """True when running from a source checkout (repo files are reachable)."""
    return (repo_root() / "ontology.json").exists()


def _packaged_data(name: str):
    """Path to a data file shipped inside the wheel, or None."""
    try:
        from importlib.resources import files
        candidate = files("slopkit") / "data" / name
        if candidate.is_file():
            return Path(str(candidate))
    except (ImportError, ModuleNotFoundError, FileNotFoundError, TypeError):
        pass
    return None


def ontology_path() -> Path:
    """Path to the canonical ontology.json (SLOP_ONTOLOGY overrides)."""
    env = os.environ.get("SLOP_ONTOLOGY")
    if env:
        return Path(env).resolve()
    root = repo_root() / "ontology.json"
    if root.exists():
        return root
    packaged = _packaged_data("ontology.json")
    if packaged:
        return packaged
    raise FileNotFoundError(
        "ontology.json not found. Set SLOP_ONTOLOGY to its path, or run the "
        "CLI from a checkout of github.com/hikaman/ai-slop-ontology.")


def _skill_scripts_dir() -> Path:
    return repo_root() / "skills" / "ai-slop-detection" / "scripts"


def _read_canonical_version():
    """Read `version: "x.y.z"` from the canonical Markdown front matter."""
    import re
    md = repo_root() / "AI-SLOP-ONTOLOGY.md"
    if not md.exists():
        md = _packaged_data("AI-SLOP-ONTOLOGY.md")
    if not md or not Path(md).exists():
        return None
    m = re.search(r'^version:\s*"([^"]+)"',
                  Path(md).read_text(encoding="utf-8"), re.MULTILINE)
    return m.group(1) if m else None


def _ensure_paths():
    for p in (repo_root() / "src", _skill_scripts_dir()):
        sp = str(p)
        if p.exists() and sp not in sys.path:
            sys.path.insert(0, sp)


def load_detectors():
    """Return (SlopClassifier, find_rhetorical_patterns, RHETORICAL_PATTERNS)."""
    try:  # installed wheel
        from slopkit.engine.classifier import SlopClassifier
        from slopkit.skill.rhetorical_patterns import (
            find_rhetorical_patterns,
            RHETORICAL_PATTERNS,
        )
    except ImportError:  # source checkout / editable install
        _ensure_paths()
        from classifier import SlopClassifier
        from rhetorical_patterns import (
            find_rhetorical_patterns,
            RHETORICAL_PATTERNS,
        )
    return SlopClassifier, find_rhetorical_patterns, RHETORICAL_PATTERNS


class Engine:
    """Composed detection front-end used by every CLI subcommand."""

    def __init__(self, ontology: Path = None):
        SlopClassifier, find_rhetorical, catalogue = load_detectors()
        self.ontology_file = Path(ontology) if ontology else ontology_path()
        self._classifier = SlopClassifier(str(self.ontology_file))
        self._find_rhetorical = find_rhetorical
        self._rhetorical_catalogue = catalogue

    # --- text ---
    def classify_text(self, text: str):
        return self._classifier.classify_text(text)

    def rhetorical(self, text: str):
        return self._find_rhetorical(text)

    # --- code ---
    def classify_code(self, code: str, language: str = ""):
        return self._classifier.classify_code(code, language)

    # --- metadata ---
    def signal_stats(self) -> dict:
        return self._classifier.get_signal_stats()

    def ontology_meta(self) -> dict:
        o = self._classifier.ontology
        version = o.get("version") or o.get("dc:version")
        if not version:
            # version is authoritative in the canonical Markdown front matter
            version = _read_canonical_version() or "?"
        return {
            "name": o.get("dc:title") or o.get("name") or "AI Slop Ontology",
            "version": version,
            "date": o.get("dc:date", "?"),
            "license": o.get("dc:license") or o.get("license") or "CC BY 4.0",
        }

    def rhetorical_catalogue(self) -> dict:
        return self._rhetorical_catalogue


@lru_cache(maxsize=None)
def get_engine(ontology: str = None) -> Engine:
    return Engine(Path(ontology) if ontology else None)
