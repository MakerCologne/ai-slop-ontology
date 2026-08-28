"""Engine adapter: locate the repo, load the canonical detectors, expose a
single composed API for the CLI.

Reuses (never re-implements):
  - src/classifier.py            → SlopClassifier (text + code, reads ontology.json)
  - skills/.../rhetorical_patterns → find_rhetorical_patterns (detect-only)
"""

import os
import sys
from functools import lru_cache
from pathlib import Path


def repo_root() -> Path:
    """Repository checkout root, or the package's parent when installed.

    Only the repo-maintenance subcommands (benchmark, selfcheck) need a real
    checkout; they check for the script and report its absence. Runtime data
    goes through `_data_root()` instead, which also works from a wheel.
    Overridable with SLOP_REPO_ROOT for unusual layouts.
    """
    env = os.environ.get("SLOP_REPO_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parent.parent


def is_installed_layout() -> bool:
    """True when running from a built wheel rather than from the checkout.

    The build copies the runtime data into `slopkit/_bundled/`
    (pyproject.toml, force-include); the directory never exists in the
    checkout, so its presence is the discriminator.
    """
    return (Path(__file__).resolve().parent / "_bundled").is_dir()


def _data_root() -> Path:
    """Directory holding src/, the skill scripts and ontology.json."""
    if os.environ.get("SLOP_REPO_ROOT"):
        return repo_root()
    bundled = Path(__file__).resolve().parent / "_bundled"
    return bundled if bundled.is_dir() else repo_root()


def ontology_path() -> Path:
    """Path to the canonical ontology.json (SLOP_ONTOLOGY overrides)."""
    env = os.environ.get("SLOP_ONTOLOGY")
    if env:
        return Path(env).resolve()
    return _data_root() / "ontology.json"


def _skill_scripts_dir() -> Path:
    root = _data_root()
    bundled = root / "skills"
    # In the wheel the scripts sit directly under _bundled/skills; in the
    # checkout they keep their full path.
    if root.name == "_bundled":
        return bundled
    return bundled / "ai-slop-detection" / "scripts"


def _read_canonical_version():
    """Read `version: "x.y.z"` from the canonical Markdown front matter."""
    import re
    md = _data_root() / "AI-SLOP-ONTOLOGY.md"
    if not md.exists():
        return None
    m = re.search(r'^version:\s*"([^"]+)"', md.read_text(encoding="utf-8"), re.MULTILINE)
    return m.group(1) if m else None


def _ensure_paths():
    for p in (_data_root() / "src", _skill_scripts_dir()):
        sp = str(p)
        if sp not in sys.path:
            sys.path.insert(0, sp)


class Engine:
    """Composed detection front-end used by every CLI subcommand."""

    def __init__(self, ontology: Path = None):
        _ensure_paths()
        from classifier import SlopClassifier  # from src/
        from rhetorical_patterns import (  # from skill scripts
            find_rhetorical_patterns,
            RHETORICAL_PATTERNS,
        )

        self.ontology_file = Path(ontology) if ontology else ontology_path()
        self._classifier = SlopClassifier(str(self.ontology_file))
        self._find_rhetorical = find_rhetorical_patterns
        self._rhetorical_catalogue = RHETORICAL_PATTERNS

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


def strip_markup(text: str) -> str:
    """Markdown input pre-pass (#69) — re-exported from the skill scripts."""
    _ensure_paths()
    from markup_prepass import strip_markup as _strip  # from skill scripts
    return _strip(text)


@lru_cache(maxsize=None)
def get_engine(ontology: str = None) -> Engine:
    return Engine(Path(ontology) if ontology else None)
