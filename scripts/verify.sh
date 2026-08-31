#!/usr/bin/env bash
# Alle acht Gates in der Reihenfolge des CI-Workflows (.github/workflows/tests.yml).
# Aufruf aus dem Repo-Wurzelverzeichnis:  bash scripts/verify.sh
#
# Solange GitHub Actions deaktiviert ist (#100), ist das der beste verfuegbare
# Nachweis — und ein Ersatz, kein Gleichwertiges: es laeuft auf deiner Umgebung,
# nicht auf einem frischen Runner. Sag das so in jedem PR.
set -u

# Aus der Repo-Wurzel aufrufen. Ohne diese Pruefung meldet das Skript acht rote
# Gates, die nur "Datei nicht gefunden" bedeuten — ein rotes Ergebnis, das
# nichts ueber das Repo aussagt, ist schlimmer als gar keins.
for required in ontology.json eval/run_benchmark.py scripts/check_ssot.py; do
  if [ ! -f "$required" ]; then
    echo "FEHLER: $required nicht gefunden."
    echo "Dieses Skript laeuft aus der Repo-Wurzel: cd <checkout> && bash scripts/verify.sh"
    exit 2
  fi
done

fail=0
step() { printf '\n=== %s ===\n' "$1"; }
check() { if [ "$1" -ne 0 ]; then echo "  ^^ FAILED"; fail=1; fi; }

step "0 Abhaengigkeiten"
python -c "import pytest, yaml; print('  pytest + pyyaml ok')" || {
  echo "  fehlt: pip install pytest pyyaml hatchling"; exit 2; }
python -c "import hatchling" 2>/dev/null && echo "  hatchling ok" \
  || echo "  WARNUNG: hatchling fehlt -> test_packaging ueberspringt die Build-Tests"

step "1 Suite"
python -m pytest -q; check $?

step "2 Datendateien"
python -c "import json; json.load(open('ontology.json')); print('  ontology.json ok')"; check $?
python -c "import yaml; yaml.safe_load(open('ai_slop_ontology.yaml')); print('  yaml ok')"; check $?

step "3 Gates"
for s in check_consistency check_ssot check_doc_signals check_methodology check_signal_dod; do
  printf '  --- %s\n' "$s"; python "scripts/$s.py"; check $?
done
printf '  --- fp_baseline --check\n'; python scripts/fp_baseline.py --check; check $?
printf '  --- run_control_set\n';    python eval/run_control_set.py | tail -3; check ${PIPESTATUS[0]}
printf '  --- self_check_docs\n';    python scripts/self_check_docs.py | tail -3; check ${PIPESTATUS[0]}

step "4 Wheel-Rauchtest ausserhalb des Checkouts"
tmp=$(mktemp -d); venv="$tmp/venv"
python -m venv "$venv" \
  && "$venv/bin/pip" install -q . \
  && printf '%s\n' "In today's rapidly evolving digital landscape, leveraging synergies is not just a strategy, it's a necessity. This rich tapestry of innovation underscores a profound transformation. Let's delve into the multifaceted realm of seamless integration." > "$tmp/sample.txt" \
  && (cd "$tmp" && "$venv/bin/slop" info | head -1 && "$venv/bin/slop" score --file sample.txt)
check $?
# Gegenprobe: --fail-over MUSS auf diesem Text greifen, sonst wurde die Datei
# nicht gelesen (ohne --file bewertet die CLI den Dateinamen als Literal).
( cd "$tmp" && "$venv/bin/slop" score --file sample.txt --fail-over 0.4 >/dev/null )
if [ $? -eq 1 ]; then echo "  fail-over greift wie erwartet"; else
  echo "  ^^ FAILED: --fail-over hat nicht gegriffen"; fail=1; fi
rm -rf "$tmp"

step "5 Benchmark-Untergrenzen"
python eval/run_benchmark.py --min-precision 1.0 --min-recall 0.99 | tail -1; check ${PIPESTATUS[0]}

printf '\n===================================\n'
if [ "$fail" -eq 0 ]; then echo "ALLE GATES GRUEN"; else echo "MINDESTENS EIN GATE ROT"; fi
exit "$fail"
