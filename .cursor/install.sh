#!/usr/bin/env bash
#
# Idempotent Cloud Agent install script for Sahay AI.
# Refreshes backend (FastAPI/venv) and frontend (Next.js/npm) dependencies
# after the repository has been checked out. Safe to run repeatedly.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Sahay AI install starting (repo: $REPO_ROOT)"

# --- System dependency: Python venv support (ensurepip) ---
# The default image ships Python 3.12 but not the venv package.
if ! python3 -m venv --help >/dev/null 2>&1 || ! dpkg -s python3.12-venv >/dev/null 2>&1; then
  echo "==> Installing python3.12-venv"
  sudo apt-get update -y
  sudo apt-get install -y python3.12-venv
fi

# --- Backend: virtualenv + Python dependencies ---
cd "$REPO_ROOT/backend"
if [ ! -d venv ]; then
  echo "==> Creating backend virtualenv"
  python3 -m venv venv
fi
# shellcheck disable=SC1091
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
deactivate

# Local dev config with sane defaults. Never overwrites an existing .env.
# Secrets (GROQ_API_KEY, SARVAM_API_KEY, SUPABASE_*) are injected as
# environment variables and take precedence over these file values.
if [ ! -f "$REPO_ROOT/backend/.env" ]; then
  echo "==> Writing backend/.env with development defaults"
  cat > "$REPO_ROOT/backend/.env" <<'ENVEOF'
DEBUG=true
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000
JWT_SECRET_KEY=dev-local-insecure-key-change-me
CHROMA_PERSIST_DIR=./data/chromadb
EMBEDDING_MODEL=intfloat/multilingual-e5-large
ENVEOF
fi

# --- Frontend: Node dependencies ---
cd "$REPO_ROOT/frontend"
echo "==> Installing frontend dependencies (npm ci)"
npm ci

echo "==> Sahay AI install complete"
