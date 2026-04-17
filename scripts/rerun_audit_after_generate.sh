#!/usr/bin/env bash
# Regenerate all meeting .docx, refresh audit_text/*.txt from them, re-render audit PDF from doc/audit_reports/*.md.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# Ensures reportlab, python-docx, etc. match pyproject.toml (avoids system python / partial venv).
poetry install --no-interaction
poetry run python corporate_meeting_minutes.py --output-root generated
poetry run python scripts/extract_audit_text.py
poetry run python scripts/audit_md_to_pdf.py
echo "Done: generated/ + audit_text/ + doc/audit_reports/senior_counsel_audit_2022_2026.pdf"
