"""DE-IDEOLOGY — detect-only Rhetorik-Layer für ideologische Ritualmuster.

Promotion von nursery (#92, PR #127) nach dem #98-Korpus-Beschluss:
46 positiv / 40 negativ (own:handwritten, adr/0005), Precision-Gate
FP=0 auf den Hard-Negatives.

10 Patterns (Katalog: skills/ai-slop-detection/references/de_ideology_patterns.json,
Coverage-Doku: docs/de-ideology-coverage.md, ADR-0008 B-Default / ADR-0006
detect-only):

  RitualFirewall, MartyrCartel, CollectiveOther, ReplacementKicker,
  EthnopluralistRebrand, PurityBan, VibeScapegoat, SalvationModel,
  UnfalsifiableTemplate, EnemyVermin

DETECT-ONLY (ADR-0001/0006): named evidence mit zitiertem Beleg,
keep_when-Pflicht je Pattern, konservativ. Findings sind advisory und
gehen NICHT in den numerischen slop_score ein; `polemic_risk` bleibt
ein separater, niemals score-wirksamer Berichtsteil.

Der Detektor bewertet die STRATEGIEFORM der Rhetorik, nicht die
Parteizugehörigkeit oder politische Position eines Autors (ADR-0008:
Vertrag aus docs/de-ideology-coverage.md).

Regex-Katalog ist corpus-kalibrierte Inline-Liste (dokumentierte
bewusste Abweichung von der ontology.json-SSOT-Projektion, siehe
scripts/check_ssot.py) — der SSOT-Spiegel lebt in ontology.json
`signals.deIdeology` für Katalog-Parität.
"""

import re

# ---------------------------------------------------------------------------
# Pattern-Katalog: (id, confidence, trigger-regexes, keep_when-regexes, label)
#
# keep_when ist PFLICHT: trifft eine keep_when-Regex ebenfalls im Text,
# wird der Fund unterdrückt (konservativ, FP-Schutz zuerst).
# ---------------------------------------------------------------------------

_PATTERNS = [
    (
        "RitualFirewall",
        0.6,
        [
            re.compile(r"die\s+brandmauer", re.I),
            re.compile(r"die\s+feuermauer", re.I),
            re.compile(r"hold\s+the\s+(?:firewall|cordon\s+santaire|sanitary\s+cordon)", re.I),
            re.compile(r"brandmauer\s+(?:halten|wahren|verteidigen)", re.I),
        ],
        [
            re.compile(r"untersuchungsausschuss", re.I),
            re.compile(r"minderheitsregierung", re.I),
            re.compile(r"verbotsverfahren", re.I),
            re.compile(r"ausschuss", re.I),
            re.compile(r"satire|ironie|parodie|glosse|ironic|parody", re.I),
        ],
        "Brandmauer als Selbstzweck",
    ),
    (
        "MartyrCartel",
        0.6,
        [
            re.compile(r"systempresse", re.I),
            re.compile(r"lügenpresse", re.I),
            re.compile(r"systemmedien", re.I),
            re.compile(r"die\s+altparteien", re.I),
            re.compile(r"das\s+kartell\s+der\s+(?:alten\s+)?parteien", re.I),
            re.compile(r"lying\s+press", re.I),
        ],
        [
            re.compile(r"aktenzeichen", re.I),
            re.compile(r"\baz\b[^a-z]", re.I),  # Aktenzeichen-Kürzel
            re.compile(r"protokoll", re.I),
            re.compile(r"beschluss", re.I),
            re.compile(r"urteil", re.I),
            re.compile(r"docket", re.I),
        ],
        "System-/Kartell-/Altparteien-Totalerklärung",
    ),
    (
        "CollectiveOther",
        0.7,
        [
            re.compile(r"die\s+migranten\s+sind", re.I),
            re.compile(r"die\s+ausländer\s+sind", re.I),
            re.compile(r"die\s+muslime\s+sind", re.I),
            re.compile(r"those\s+(?:migrants|immigrants|refugees)\s+are", re.I),
            re.compile(r"die\s+sind\s+nun\s+mal\s+so", re.I),
        ],
        [
            # Statistik mit Nenner/Zeitraum/Quelle
            re.compile(r"\d+\s*%"),
            re.compile(r"\b(19|20)\d{2}\b"),
            re.compile(r"quelle|source|destatis|eurostat|bamf|lizenz", re.I),
        ],
        "Herkunft als Kollektivschuld",
    ),
    (
        "ReplacementKicker",
        0.7,
        [
            re.compile(r"umvolkung", re.I),
            re.compile(r"bevölkerungsaustausch", re.I),
            re.compile(r"great\s+replacement", re.I),
            re.compile(r"der\s+austausch\s+des\s+volkes", re.I),
            re.compile(r"das\s+land,?\s+das\s+wir\s+kannten", re.I),
        ],
        [
            re.compile(r"\b(19|20)\d{2}\b"),
            re.compile(r"geburtenrate|wanderungssaldo|demografi|destatis|eurostat", re.I),
            re.compile(r"quelle|source", re.I),
        ],
        "Bevölkerungsaustausch als Schluss",
    ),
    (
        "EthnopluralistRebrand",
        0.6,
        [
            re.compile(r"recht\s+auf\s+differenz", re.I),
            re.compile(r"ethnopluralis", re.I),
            re.compile(r"ethno-differentialis", re.I),
            re.compile(r"trennung\s+der\s+kulturen", re.I),
            re.compile(r"getrennte\s+räume", re.I),
            re.compile(r"echte\s+vielfalt\s+lebt\s+von\s+der\s+trennung", re.I),
            re.compile(r"each\s+culture\s+its\s+own", re.I),
        ],
        [
            re.compile(r"ethnografi|völkerkund|ethnolog", re.I),
            re.compile(r"studie|studium|forschung", re.I),
        ],
        "Diversität = Trennung (Ethnopluralismus-Rebrand)",
    ),
    (
        "PurityBan",
        0.6,
        [
            re.compile(r"\bai\s+is\s+theft\b", re.I),
            re.compile(r"totalverbot", re.I),
            re.compile(r"komplett\s*verbieten\s+lassen", re.I),
            re.compile(r"ban\s+all\s+ai", re.I),
        ],
        [
            re.compile(r"urheberrecht|copyright|verfahren|klage|gericht|lawsuit|case\b", re.I),
            re.compile(r"dokumentiert", re.I),
        ],
        "Totalverbot statt Differenzierung",
    ),
    (
        "VibeScapegoat",
        0.6,
        [
            re.compile(r"vibe[- ]cod(?:ed|ing)\s+slop\s+devs", re.I),
            re.compile(r"vibe[- ]cod(?:ed|ing)\s+devs", re.I),
            re.compile(r"slop\s+devs\s+at\s+work", re.I),
        ],
        [
            re.compile(r"postmortem|post-mortem", re.I),
            re.compile(r"\bdiff\b|\bcommit\b|regression|incident", re.I),
        ],
        "Jeder Ausfall = Vibe Coding",
    ),
    (
        "SalvationModel",
        0.6,
        [
            re.compile(r"nur\s+noch\s+\S+(?:\s+\S+){0,3}\s+kann\s+das\s+land\s+retten", re.I),
            re.compile(r"nur\s+(?:noch\s+)?\S+(?:\s+\S+){0,3}\s+kann\s+uns\s+(?:noch\s+)?retten", re.I),
            re.compile(r"only\s+\S+\s+can\s+save\s+(?:us|the\s+country|america|europe)", re.I),
            re.compile(r"alle\s+anderen\s+sind\s+teil\s+des\s+problems", re.I),
        ],
        [
            re.compile(r"\b(wenn|falls|if)\b.{0,80}\b(test|eval|benchmark|bedingung)", re.I),
            re.compile(r"wahlprognose|umfrage|belegt", re.I),
            re.compile(r"satire|ironie|parodie|glosse|ironic|parody", re.I),
        ],
        "Modell/Partei als Erlöser",
    ),
    (
        "UnfalsifiableTemplate",
        0.6,
        [
            re.compile(r"bestätigt\s+nur,?\s+was\s+wir\s+(?:immer\s+)?gesagt\s+haben", re.I),
            re.compile(r"genau\s+wie\s+wir\s+es\s+(?:immer\s+)?gesagt\s+haben", re.I),
            re.compile(r"proves?\s+(?:what|that)\s+we'?ve\s+been\s+saying", re.I),
            re.compile(r"zeigt\s+nur,?\s+was\s+wir\s+schon\s+immer\s+wussten", re.I),
        ],
        [
            re.compile(r"\b(19|20)\d{2}\b"),
            re.compile(r"\d{2}\.\d{2}\."),
            re.compile(r"zum\s+ersten\s+mal|neue\s+information|erstmals", re.I),
        ],
        "Jedes Event bestätigt den Frame",
    ),
    (
        "EnemyVermin",
        0.7,
        [
            re.compile(r"ungeziefer", re.I),
            re.compile(r"untermensch", re.I),
            re.compile(r"volksschädling", re.I),
            re.compile(r"\bparasiten\s+des\s+volkes\b", re.I),
            re.compile(r"\bvermin\b", re.I),
            re.compile(r"\bcockroaches\b", re.I),
            re.compile(r"\brats\b.{0,30}\b(infest|plague|immigra)", re.I),
        ],
        [
            re.compile(r"satire|ironie|ironic|parodie|parody|glosse", re.I),
            re.compile(r"historisch|analyse|sprachgebrauch|forschung|studie", re.I),
            re.compile(r"\b(19|20)\d{2}\b"),
            re.compile(r"\"[^\"]{0,80}\""),  # wörtliches Zitat (Fremdrede markiert)
        ],
        "Entmenschlichung",
    ),
]

# Kompilierter Katalog als strukturierte Liste
CATALOG = [
    {"id": pid, "confidence": conf, "label": label}
    for pid, conf, _t, _k, label in _PATTERNS
]


class DeIdeologyFinding:
    """Ein advisory Fund: Pattern-ID, Konfidenz, zitiertes Belegstück."""

    __slots__ = ("pattern_id", "label", "confidence", "evidence")

    def __init__(self, pattern_id: str, label: str, confidence: float, evidence: str):
        self.pattern_id = pattern_id
        self.label = label
        self.confidence = confidence
        self.evidence = evidence

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"DeIdeologyFinding({self.pattern_id!r}, conf={self.confidence}, "
            f"evidence={self.evidence!r})"
        )

    def to_dict(self) -> dict:
        return {
            "pattern_id": self.pattern_id,
            "label": self.label,
            "confidence": self.confidence,
            "evidence": self.evidence,
        }


class DeIdeologyClassifier:
    """Detect-only Klassifikator für ideologische Ritualmuster (#92).

    Findings sind advisory (named evidence), niemals score-wirksam.
    Der Detektor bewertet Strategieform, nicht Parteizugehörigkeit.
    """

    score_effect = "none (detect-only, named evidence)"

    def classify_text(self, text: str) -> list:
        findings = []
        for pid, conf, triggers, keeps, label in _PATTERNS:
            hit = None
            for rx in triggers:
                m = rx.search(text)
                if m:
                    hit = m
                    break
            if hit is None:
                continue
            # keep_when-Pflicht: konservativ unterdrücken
            if any(k.search(text) for k in keeps):
                continue
            snippet = text[max(0, hit.start() - 30): hit.end() + 30].strip()
            findings.append(DeIdeologyFinding(pid, label, conf, f"…{snippet}…"))
        return findings
