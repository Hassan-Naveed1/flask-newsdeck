#!/usr/bin/env bash
# Dev runner with cross-platform venv activation (Windows Git Bash + macOS/Linux).
# Usage:
#   chmod +x run.sh
#   ./run.sh

set -euo pipefail

# 1) Ensure venv exists
if [ ! -d ".venv" ]; then
  python -m venv .venv 2>/dev/null || python3 -m venv .venv
fi

# 2) Activate venv (prefer Unix path, then Windows Git Bash path)
if [ -f ".venv/bin/activate" ]; then
  # macOS/Linux
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
elif [ -f ".venv/Scripts/activate" ]; then
  # Windows (Git Bash)
  # shellcheck disable=SC1091
  source ".venv/Scripts/activate"
else
  echo "Warning: could not find venv activate script; continuing without activation."
fi

# 3) Install deps if Flask isn’t available yet
python -c "import flask" 2>/dev/null || pip install -r requirements.txt

# 4) Ensure .env exists (copy once if missing)
[ -f .env ] || cp .env.example .env

# 5) Minimal sanity check for NEWSAPI_KEY
if ! grep -qE '^NEWSAPI_KEY=' .env; then
  echo "Note: NEWSAPI_KEY not found in .env; scheduler will skip fetches until it is set."
fi

# 6) Initialize DB schema (idempotent)
python - <<'PY'
from models import init_db
init_db()
PY

# 7) Start Flask dev server
export FLASK_APP=app
flask --app app run
