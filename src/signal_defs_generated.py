"""
GENERATED FILE — DO NOT EDIT BY HAND.

Data-only projection of ontology.json (source of truth), produced by
scripts/generate_signal_defs.py (issue #49). Regenerate with:

    python3 scripts/generate_signal_defs.py

No code, no detection behavior. Detection modules still carry their
corpus-calibrated inline lists (see scripts/check_ssot.py for the
register of conscious deviations); full migration onto this view is a
documented follow-up, not part of #49.
"""

COUNTERMEASURES = [
  "detection",
  "platforms",
  "risks",
  "userAgentLevel"
]

DETECTION_SIGNALS_STRUCTURED = {
  "behavioral": [
    {
      "relevance": "Massenerzeugung",
      "signal": "sehr hohe Upload-Frequenz"
    },
    {
      "relevance": "Content-Farm",
      "signal": "viele ähnliche Titel/Thumbnails"
    },
    {
      "relevance": "Reichweiten- oder SEO-Spiel",
      "signal": "Crossposting auf vielen Domains"
    },
    {
      "relevance": "Opportunismus",
      "signal": "plötzliche Themenwechsel"
    },
    {
      "relevance": "Slop Producer",
      "signal": "neue Accounts mit hoher Outputrate"
    },
    {
      "relevance": "Citation Inflation",
      "signal": "Cluster mit gegenseitigen Zitaten"
    }
  ],
  "content_based": [
    {
      "relevance": "oft Text-Slop",
      "signal": "generische Sprache"
    },
    {
      "relevance": "hohes RAG-Risiko",
      "signal": "fehlende Primärquellen"
    },
    {
      "relevance": "akademischer / rechtlicher Hochrisikofall",
      "signal": "halluzinierte Zitate"
    },
    {
      "relevance": "schwache Validierung",
      "signal": "widersprüchliche Details"
    },
    {
      "relevance": "superficial competence",
      "signal": "überperfekte Banalität"
    },
    {
      "relevance": "keine echte Autorschaft",
      "signal": "wenig konkrete Erfahrung"
    },
    {
      "relevance": "Template- oder Serienproduktion",
      "signal": "wiederholte Struktur"
    }
  ],
  "provenance": [
    {
      "relevance": "nützlich, aber nicht ausreichend",
      "signal": "C2PA vorhanden"
    },
    {
      "relevance": "nützlich, aber nicht vollständig",
      "signal": "Wasserzeichen / SynthID"
    },
    {
      "relevance": "hilfreich, aber inkonsistent",
      "signal": "Plattformlabel"
    },
    {
      "relevance": "Verdacht",
      "signal": "fehlende Autorschaft"
    },
    {
      "relevance": "starker Verdacht",
      "signal": "falsche Autorschaft"
    },
    {
      "relevance": "eher entlastend",
      "signal": "offengelegter KI-Einsatz + Human Review"
    }
  ]
}

ONTOLOGY_DATE = "2026-08-25"

ONTOLOGY_TITLE = "AI Slop Ontology"

RHETORICAL_PATTERNS = []

SLOP_TYPES = [
  "AUDIO_SLOP",
  "BY_FORM",
  "BY_PURPOSE",
  "CODE_SLOP",
  "DOMAIN_SLOP",
  "IMAGE_SLOP",
  "TEXT_SLOP",
  "VIDEO_SLOP"
]
