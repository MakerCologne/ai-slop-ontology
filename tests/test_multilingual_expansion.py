"""Tests für die #53-Spracherweiterung: ZH/JA/PT/IT/RU/AR/TR-Marker-Sets.

DoD je Sprache: 2 Positive (>=2 Marker -> Multilingual_<lang>-Signal in
Classifier UND Skill-Scorer-Hit) + 1 Hard-Negative (sauberer Muttersprach-
text -> kein Signal) + Paritäts-Gate (ontology.json == slop_scorer).

CJK-Spezialfall: Marker müssen auch mitten im laufenden (raumlosen) CJK-Text
matchen — keine \b-Wortgrenzen an nicht-ASCII-Kanten (#53 _term_pattern-Fix).
"""

import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, ROOT)

import slop_scorer  # noqa: E402
from classifier import SlopClassifier  # noqa: E402

NEW_LANGS = ["chinese", "japanese", "portuguese", "italian",
             "russian", "arabic", "turkish"]

# Positive Testtexte: je 3 Marker der jeweiligen Sprache in natürlichem
# Fließtext (KEINE isolierte Marker-Aneinanderreihung — Match muss im
# Satzzusammenhang gelingen, inkl. CJK ohne Leerzeichen).
POSITIVES = {
    "chinese": (
        "在当今快速发展的世界中，数据整合发挥着至关重要的作用。值得注意的是，"
        "这一变化是不可否认的，需要整体而言加以审视。"
    ),
    "japanese": (
        "デジタル時代において、この技術は重要な役割を果たしている。"
        "結論として、シームレスな統合が包括的な価値を生むと考えられる。"
    ),
    "portuguese": (
        "No mundo acelerado de hoje, é importante notar que a análise de dados "
        "desempenha um papel crucial. Em conclusão, uma abordagem holística é "
        "inegável para o sucesso."
    ),
    "italian": (
        "Nel mondo frenetico di oggi, è importante notare che la tecnologia "
        "svolge un ruolo cruciale. In conclusione, un approccio olistico "
        "offre un'esperienza senza soluzione di continuità."
    ),
    "russian": (
        "В современном быстро меняющемся мире важно отметить, что данные "
        "играют ключевую роль. В заключение можно сказать, что бесшовный "
        "целостный подход невозможно отрицать."
    ),
    "arabic": (
        "في عالم اليوم سريع التغير، من المهم أن نلاحظ أن التحول الرقمي "
        "يلعب دورًا محوريًا. في الختام، لا يمكن إنكار أهمية نهج شامل."
    ),
    "turkish": (
        "Günümüzün hızla değişen dünyasında dikkat çekmek gerekir ki: dijital "
        "çağda veriler çok önemli bir rol oynuyor. Sonuç olarak, bütüncül bir "
        "yaklaşım inkar edilemez."
    ),
}

# Hard Negatives: natürlicher, marker-freier Muttersprachtext.
NEGATIVES = {
    "chinese": "我今天去了市场，买了苹果和梨。天气很好，路上遇见了老朋友。",
    "japanese": "昨日は近所の bakery でパンを買って、公園を散歩した。天気が良かった。",
    "portuguese": (
        "Ontem fui ao mercado com a minha vizinha e comprámos tomates, "
        "azeite e um melão maduro para o almoço de domingo."
    ),
    "italian": (
        "Ieri sono passato dal panettiere sotto casa e ho preso il pane, "
        "due mele e il giornale. Poi ho salutato il Signor Bruno."
    ),
    "russian": (
        "Вчера я зашёл в булочную на углу, купил чёрный хлеб, яблоки и "
        "молоко, а по дороге домой встретил соседа."
    ),
    "arabic": (
        "ذهبت أمس إلى السوق واشتريت خبزًا وتفاحًا ولبنًا، ثم قابلت جاري "
        "في الطريق ورجعت إلى البيت قبل الغروب."
    ),
    "turkish": (
        "Dün evin altındaki fırından ekmek ve iki elma aldım, dönüşte "
        "komşuya selam verip eve girdim."
    ),
}


@pytest.mark.parametrize("lang", NEW_LANGS)
def test_positive_classifier_signal(lang):
    clf = SlopClassifier()
    result = clf.classify_text(POSITIVES[lang])
    ids = [s.signal_id for s in result.signals_detected]
    assert f"Multilingual_{lang}" in ids, (
        f"expected Multilingual_{lang}, got {ids}"
    )


@pytest.mark.parametrize("lang", NEW_LANGS)
def test_positive_skill_scorer(lang):
    hits = slop_scorer.multilingual_buzzword_score(POSITIVES[lang])
    assert lang in hits and len(hits[lang]) >= 2, f"{lang}: {hits.get(lang)}"


@pytest.mark.parametrize("lang", NEW_LANGS)
def test_negative_clean_native_text(lang):
    clf = SlopClassifier()
    result = clf.classify_text(NEGATIVES[lang])
    ids = [s.signal_id for s in result.signals_detected]
    assert f"Multilingual_{lang}" not in ids, ids
    hits = slop_scorer.multilingual_buzzword_score(NEGATIVES[lang])
    assert lang not in hits


def test_cjk_marker_matches_inside_running_text():
    # CJK-Marker müssen OHNE Wortgrenzen im zusammenhängenden Text matchen
    # (kein Leerzeichen vor dem Marker, kein Punkt nach dem Marker nötig).
    text = "首先要说的是，在当今快速发展的世界中技术改变了工作方式。"
    hits = slop_scorer.multilingual_buzzword_score(text)
    assert "chinese" in hits and "在当今快速发展的世界中" in hits["chinese"]


def test_ascii_boundaries_still_enforced():
    # Regressionsschutz: ASCII-Terms matchen weiterhin nur an Wortgrenzen.
    pat = slop_scorer._term_pattern("delve")
    assert re.search(pat, "the delved artifact") is None
    assert re.search(pat, "let us delve deeper") is not None


def test_parity_ontology_vs_scorer():
    with open(os.path.join(ROOT, "ontology.json")) as f:
        oj = json.load(f)
    json_langs = {k for k, v in oj["signals"]["multilingual"].items()
                  if isinstance(v, dict) and "buzzwords" in v}
    assert json_langs == set(slop_scorer.MULTILINGUAL_BUZZWORDS)
    for lang in NEW_LANGS:
        assert (oj["signals"]["multilingual"][lang]["buzzwords"]
                == slop_scorer.MULTILINGUAL_BUZZWORDS[lang])


import re  # noqa: E402  (benutzt in test_ascii_boundaries_still_enforced)
