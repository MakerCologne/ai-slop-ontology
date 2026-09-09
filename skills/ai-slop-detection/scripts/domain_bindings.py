#!/usr/bin/env python3
"""Domain bindings for the AI-slop skill scorer (issue #35).

Slop defaults are domain-conditional (unslop: "If the page is for devtools
→ ..."). Static signals without domain context produce systematic false
positives/negatives. ``ontology.json`` therefore carries an optional
``triggered_by: domain`` metadata block per signal (``domainBindings``);
this module is the thin, data-driven accessor for it.

Semantics (documented in ontology.json ``domainBindings.note``):

- A signal with ``applies_to`` (whitelist) is only scored in the listed
  domains; ``restricted_in`` (blacklist) suppresses it in the listed
  domains. Whitelist beats blacklist (``applies_to`` wins) when both are
  given.
- Signals without ``triggered_by`` are domain-agnostic — the default, so
  the engine does not drift for callers that pass no domain.
- The scorer applies bindings at two levels: named-signal findings
  (classifier level, filter by ``signal_id``) and score dimensions
  (``SIGNAL_WEIGHT_MAP`` below zeroes the mapped weight keys for gated
  signals). All opt-in via ``--domain NAME`` / ``slop_score(domain=...)``;
  fail-loud on unknown domains.
"""

import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
# references/ontology.json is a symlink to the root ontology.json (SSOT #49)
_ONTOLOGY = os.path.join(_HERE, "..", "references", "ontology.json")

# Engine-config: maps named signals (severity taxonomy / classifier
# signal_id) to the scorer weight dimensions they feed. Only signals with a
# domain binding belong here. Registered in scripts/check_ssot.py.
SIGNAL_WEIGHT_MAP = {
    "Workslop": ("phrases",),
    "PeerReviewSlop": ("phrases",),
    "SecurityReportSlop": ("phrases",),
    "NumberedListOveruse": ("list_heavy",),
    "FakeAuthoritySlop": ("fake_authority",),
}

_cache = None


def _load():
    global _cache
    if _cache is None:
        with open(_ONTOLOGY, encoding="utf-8") as fh:
            _cache = json.load(fh).get("domainBindings", {})
    return _cache


def get_domains():
    """Known domain names (validated, fail-loud on unknown input)."""
    return list(_load().get("domains", []))


def get_bindings():
    """Raw signal -> binding mapping from ontology.json (SSOT data)."""
    return dict(_load().get("signals", {}))


def signal_active_in(signal_id, domain):
    """True if ``signal_id`` fires in ``domain`` (default: agnostic)."""
    if domain is None:
        return True
    b = get_bindings().get(signal_id)
    if not b or b.get("triggered_by") != "domain":
        return True
    applies = b.get("applies_to")
    if applies is not None:  # whitelist wins
        return domain in applies
    return domain not in b.get("restricted_in", [])


def gated_signals(domain):
    """Signal ids that do NOT fire in ``domain``."""
    if domain is None:
        return []
    return [sid for sid in get_bindings()
            if not signal_active_in(sid, domain)]


def weight_dims_gated(domain):
    """Scorer weight dimensions zeroed for gated signals in ``domain``."""
    dims = []
    for sid in gated_signals(domain):
        for dim in SIGNAL_WEIGHT_MAP.get(sid, ()):
            if dim not in dims:
                dims.append(dim)
    return dims


def validate_domain(domain):
    """Fail-loud: unknown domains abort instead of silently no-op'ing."""
    if domain is not None and domain not in get_domains():
        raise ValueError(
            "Unknown domain %r — known: %s" % (domain, ", ".join(get_domains())))
