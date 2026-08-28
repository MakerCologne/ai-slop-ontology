# ACCESS.md — was die Umgebung kann, und was nicht

Aus einer Claude-Code-Remote-Session am 2026-08-28. Deine Umgebung kann abweichen — prüf die Punkte unter „Beim Start prüfen", statt sie zu glauben.

---

## Was funktioniert hat

**Git.** Klonen, committen, pushen, Branches anlegen, `--force-with-lease`. Der Checkout liegt unter `/home/user/ai-slop-ontology`.

**GitHub über MCP** (`mcp__github__*`). Genutzt und bestätigt:

| Aufgabe | Werkzeug |
|---|---|
| Issues lesen, anlegen, ändern, schließen | `issue_read`, `issue_write` |
| Labels setzen | `issue_write` mit `labels` — **nicht existierende Labels werden automatisch angelegt** (`P0` entstand so) |
| Sub-Issues verknüpfen | `issue_write` mit `parent_issue_number` |
| Kommentare | `add_issue_comment` (funktioniert auch auf PRs) |
| PRs anlegen, lesen, schließen, mergen | `create_pull_request`, `pull_request_read`, `update_pull_request`, `merge_pull_request` |
| Workflow-Läufe und Logs | `actions_list`, `get_job_logs` mit `failed_only` und `return_content` |

**Python.** 3.11. Die Engine braucht nur die Standardbibliothek.

## Was nicht funktioniert hat

**`gh` CLI gibt es nicht.** Alles über die MCP-Werkzeuge. Skripte aus fremden Handover-Paketen, die `gh` aufrufen, laufen hier nicht — Inhalt übernehmen, Mechanik ersetzen.

**Workflows aktivieren geht nicht.** Es gibt kein MCP-Werkzeug für `PUT /actions/workflows/{id}/enable`. Genau das blockiert #100. Wenn deine Umgebung mehr kann, ist das dein erster Gewinn.

**Pushes lösen keine Workflows aus.** Der Push läuft über ein App-Token; GitHub unterdrückt dafür Workflow-Trigger. Deshalb hat #99 `workflow_dispatch` in den Workflow ergänzt — ohne das gäbe es überhaupt keinen Weg, einen Lauf zu starten.

**`pip install .` mit `--no-build-isolation`** schlägt auf dem Debian-gepatchten setuptools mit `AttributeError: install_layout` fehl. Kein Repo-Defekt; hatchling umgeht es. Relevant nur, falls du am Packaging arbeitest.

## Nicht vorinstalliert

```
pip install pytest hatchling
```

`pytest` fehlt und die Suite braucht es (12 Dateien sind pytest-Funktionsstil). `hatchling` ist das Build-Backend; ohne es überspringt `tests/test_packaging.py` seine Build-Tests. Auf diesem Image war `pip install hatchling` erst mit `--ignore-installed` erfolgreich, weil ein von Debian verwaltetes `packaging` im Weg stand.

`pyyaml` war vorhanden. Ohne es überspringt `check_consistency.py` still den YAML-Versionsvergleich — also mit installieren, sonst prüfst du weniger, als du denkst.

## Beim Start prüfen

```bash
python --version
python -c "import pytest, hatchling, yaml; print('deps ok')"
git -C /home/user/ai-slop-ontology log --oneline -1     # erwartet: bffcc00 oder später
bash scripts/verify.sh
```

Und die eine Frage, die deine ganze Session prägt:

```
Ist der tests-Workflow aktiv?
```

Wenn ja, hast du echte CI und kannst normal arbeiten. Wenn nein, gilt `HANDOVER.md` §2: lokal messen, im PR ausweisen, #100 offen halten.

## Laufzeiten

Die volle Suite braucht 70–110 Sekunden — mehrere Tests bauen ein Wheel oder starten Subprozesse. Bei einem 2-Minuten-Timeout läuft sie knapp ins Limit; setz das Timeout großzügig oder lass sie im Hintergrund laufen. Die Gate-Skripte einzeln sind schnell (< 10 s), außer `run_benchmark.py` (~15 s).

## Hinweis zur Sitzungsform

Der Container ist ephemer. Alles, was überleben soll, muss committed und gepusht sein — ein Ergebnis, das nur im Arbeitsverzeichnis liegt, ist mit der Session weg. Das gilt auch für dieses Paket.
