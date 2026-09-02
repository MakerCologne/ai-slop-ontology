#!/usr/bin/env python3
"""Count detection signals in ontology.json with a documented, reproducible rule (#70).

Zaehlregel (dokumentiert, maschinell):
  1. signals.<medium>.<family>.indicators[]      -> 1 je Eintrag
     (families: structural, punctuation, ...; alle Medien: text/image/video/code/audio/multilingual)
  2. signals.text.buzzwords.tiers.<tier>.items[] -> 1 je Phrase (Phrase-Signal)
  3. signals.text.phrases.categories.<cat>.items[] -> 1 je Phrase
  4. signals.text.typePatterns.types.<type>      -> 1 je Typ
  5. signals.text.rhetoricalPatterns.patterns.<id> -> 1 je Pattern (detect-only, eigener Kanal)

Ausgabe: JSON {total, by_channel, detect_only}; Exit 0 immer (Report-Tool, kein Gate).
Usage: python scripts/count_signals.py [--root .]
"""
import argparse, json, os

CHANNELS = ["text", "image", "video", "code", "audio", "multilingual"]


def count(doc):
    out = {"by_channel": {}, "detect_only": 0}
    sig = doc.get("signals", {})
    for ch in CHANNELS:
        block = sig.get(ch)
        if not isinstance(block, dict):
            continue
        n = 0
        if isinstance(block.get("indicators"), list):
            n += len(block["indicators"])
        for key, val in block.items():
            if isinstance(val, dict) and isinstance(val.get("indicators"), list):
                n += len(val["indicators"])
        if ch == "text":
            bw = block.get("buzzwords", {}).get("tiers", {})
            for tier in bw.values():
                n += len(tier.get("items", []))
            ph = block.get("phrases", {}).get("categories", {})
            for cat in ph.values():
                n += len(cat.get("items", []))
            n += len(block.get("typePatterns", {}).get("types", {}))
            rp = block.get("rhetoricalPatterns", {}).get("patterns", {})
            rp_n = len(rp)
            out["detect_only"] += rp_n
            n += rp_n
        out["by_channel"][ch] = n
    out["total"] = sum(out["by_channel"].values())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    with open(os.path.join(args.root, "ontology.json"), encoding="utf-8") as f:
        doc = json.load(f)
    print(json.dumps(count(doc), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
