"""slopkit — a small toolkit + CLI over the AI Slop Ontology.

Wraps the canonical detection engine (src/) and the detect-only rhetorical
pattern module, exposing them behind a single `slop` command. The ontology data
files remain the source of truth; this package adds no new detection logic of
its own beyond composition.
"""

__version__ = "0.1.0"

from ._engine import (
    Engine,
    get_engine,
    repo_root,
    ontology_path,
)

__all__ = ["Engine", "get_engine", "repo_root", "ontology_path", "__version__"]
