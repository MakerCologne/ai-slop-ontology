"""Central decision-threshold configuration (issue #157 / GL #10).

Every script that applies the decision threshold — calibration, benchmark,
doc self-check, the irony loop's sweep basis — must read the value from
``config/threshold.json`` instead of a local constant. The threshold sweep
(GL #6.3) updates that one file; nothing else.

Why hard failure instead of a default: the failure mode this module exists
to prevent is *silent divergence* — two scripts measuring against different
operating points while both claim to measure against the official one. A
missing config with a baked-in fallback is exactly that divergence, so a
missing or malformed config aborts loudly, analogous to the key-hygiene
check.
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "config", "threshold.json")

VALID_RANGE = (0.0, 1.0)


class ThresholdConfigError(SystemExit):
    """Raised (as exit) on missing/invalid config — never a silent default."""


def load_threshold(path: str = CONFIG_PATH) -> float:
    """Return the decision threshold from the central config.

    Exits with a clear message when the file is missing, unreadable,
    structurally wrong, or out of range. Bounded to (0, 1) exclusive at the
    ends: 0 or 1 are degenerate operating points (flag everything / flag
    nothing) and almost always mean a sweep wrote a wrong axis value.
    """
    if not os.path.isfile(path):
        sys.exit(
            f"threshold config missing: {path}\n"
            "config/threshold.json is the single source of truth for the "
            "decision threshold (issue #157). Restore it — do not add a "
            "fallback default; a silent default is the divergence this "
            "config exists to prevent."
        )
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        sys.exit(f"threshold config is not valid JSON ({path}): {exc}")

    if not isinstance(data, dict) or not isinstance(data.get("threshold"), (int, float)) \
            or isinstance(data.get("threshold"), bool):
        sys.exit(
            f"threshold config must be an object like "
            f'{{"threshold": 0.40}} with a numeric "threshold" field ({path})'
        )
    value = float(data["threshold"])
    if not (VALID_RANGE[0] < value < VALID_RANGE[1]):
        sys.exit(
            f"threshold out of range (0, 1) exclusive: {value} ({path}) — "
            "a sweep axis write error, not a valid operating point"
        )
    return value
