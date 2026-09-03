# Signal-Bestätigung: ≥ 2 unabhängige Nachweise vor jedem Fix (#58)

**Status:** spec · **Vorbild:** SelfCheckGPT-Mechanik (Manakul et al., arXiv:2303.08896) · **Verwandt:** #57 (Layer 2), Kollisions-Matrix #46

## Regel

Ein Signal triggert einen Fix erst ab **2 unabhängigen Nachweisen**:
1. deterministischer Matcher (Phrase/Struktur) **und** LLM-Befund (#57), oder
2. deterministischer Matcher **und** Resample-Variante (identischer Befund bei Perturbation des Eingabetexts, z. B. Whitespace/Synonym-Perturbation).

## Metrik

FP-Fix-Rate vor/nach auf dem Benchmark-Korpus (`eval/corpus.jsonl`): Ziel FP-Fixes −50 % bei Recall-Verlust ≤ 2 Punkte; Report-Feld `evidence: [nachweis_1, nachweis_2]` je Fix-Trigger. Implementierung `confirm.py` (Loop-Issue).
