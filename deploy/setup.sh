#!/usr/bin/env bash
# setup.sh — Bootstrap the GDDL Demon Recommender backend on a fresh Ubuntu 22.04 VM.
# Tested on Oracle Cloud Always Free (VM.Standard.A1.Flex, ARM/Ampere).
#
# Usage:
#   chmod +x deploy/setup.sh
#   ./deploy/setup.sh
#
# After this script completes:
#   1. Edit .env to add your GDDL_API_KEY
#   2. Run:  source venv/bin/activate && python backend/sync.py
#   3. Run:  sudo systemctl start gddl-recommender

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_FILE="deploy/gddl-recommender.service"

echo "==> Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

echo "==> Installing Python 3.11, pip, and git..."
sudo apt-get install -y python3.11 python3.11-venv python3-pip git iptables-persistent

echo "==> Creating Python virtual environment..."
cd "$REPO_DIR"
python3.11 -m venv venv
source venv/bin/activate

echo "==> Installing backend dependencies (this may take a few minutes)..."
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "==> Setting up environment file..."
if [ ! -f .env ]; then
  cp .env.example .env
  echo ""
  echo "  [!] .env created from .env.example"
  echo "  [!] Open .env and set your GDDL_API_KEY before running sync.py"
  echo ""
else
  echo "  .env already exists, skipping."
fi

echo "==> Opening port 8000 in OS firewall..."
sudo iptables -I INPUT -p tcp --dport 8000 -j ACCEPT
sudo netfilter-persistent save

echo "==> Installing systemd service..."
# Substitute the actual user and repo path into the service file template
CURRENT_USER="$(whoami)"
sed \
  -e "s|{USER}|${CURRENT_USER}|g" \
  -e "s|{REPO_DIR}|${REPO_DIR}|g" \
  "$REPO_DIR/$SERVICE_FILE" \
  | sudo tee /etc/systemd/system/gddl-recommender.service > /dev/null

sudo systemctl daemon-reload
sudo systemctl enable gddl-recommender

echo ""
echo "============================================================"
echo " Setup complete!"
echo "============================================================"
echo ""
echo " Next steps:"
echo "   1. Edit .env and set GDDL_API_KEY:"
echo "      nano ${REPO_DIR}/.env"
echo ""
echo "   2. Populate the ChromaDB database:"
echo "      source ${REPO_DIR}/venv/bin/activate"
echo "      python ${REPO_DIR}/backend/sync.py"
echo ""
echo "   3. Start the API server:"
echo "      sudo systemctl start gddl-recommender"
echo "      sudo systemctl status gddl-recommender"
echo ""
echo "   4. Verify it's running:"
echo "      curl http://localhost:8000/health"
echo ""
