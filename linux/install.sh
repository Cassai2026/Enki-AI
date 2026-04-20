#!/usr/bin/env bash
# =============================================================================
# Enki-AI Linux Setup Script
# =============================================================================
#
# Installs all system dependencies, Piper TTS (Linux binary), Python deps,
# and optionally registers systemd services for each Enki agent.
#
# Usage:
#   chmod +x linux/install.sh
#   ./linux/install.sh [--no-systemd] [--no-piper] [--dev]
#
# Options:
#   --no-systemd   Skip systemd service installation
#   --no-piper     Skip Piper TTS download
#   --dev          Install development/testing dependencies too
#
# Requirements:
#   - Ubuntu 20.04+ / Debian 11+ / Fedora 36+ / Arch Linux
#   - Python 3.10+
#   - sudo access
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; NC='\033[0m'

info()    { echo -e "${CYAN}[ENKI]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERR]${NC}   $*" >&2; }

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
INSTALL_SYSTEMD=true
INSTALL_PIPER=true
DEV_MODE=false

for arg in "$@"; do
  case $arg in
    --no-systemd) INSTALL_SYSTEMD=false ;;
    --no-piper)   INSTALL_PIPER=false ;;
    --dev)        DEV_MODE=true ;;
    *) warn "Unknown argument: $arg" ;;
  esac
done

# ---------------------------------------------------------------------------
# Detect package manager
# ---------------------------------------------------------------------------
detect_pkg_manager() {
  if command -v apt-get &>/dev/null; then echo "apt"
  elif command -v dnf &>/dev/null;   then echo "dnf"
  elif command -v pacman &>/dev/null; then echo "pacman"
  else echo "unknown"; fi
}
PKG_MGR=$(detect_pkg_manager)
info "Detected package manager: $PKG_MGR"

# ---------------------------------------------------------------------------
# System dependencies
# ---------------------------------------------------------------------------
install_system_deps() {
  info "Installing system dependencies…"
  case $PKG_MGR in
    apt)
      sudo apt-get update -qq
      sudo apt-get install -y --no-install-recommends \
        python3 python3-pip python3-venv \
        alsa-utils pulseaudio-utils \
        libsqlite3-dev build-essential \
        curl wget unzip \
        xdg-utils \
        libasound2-dev portaudio19-dev
      ;;
    dnf)
      sudo dnf install -y \
        python3 python3-pip python3-virtualenv \
        alsa-utils pulseaudio-utils \
        sqlite-devel gcc \
        curl wget unzip \
        xdg-utils \
        alsa-lib-devel portaudio-devel
      ;;
    pacman)
      sudo pacman -Sy --noconfirm \
        python python-pip \
        alsa-utils pulseaudio \
        sqlite base-devel \
        curl wget unzip \
        xdg-utils \
        alsa-lib portaudio
      ;;
    *)
      warn "Unknown package manager — skipping system deps. Install manually:"
      warn "  python3, python3-pip, alsa-utils, portaudio, xdg-utils, sqlite3"
      ;;
  esac
  success "System dependencies installed."
}

# ---------------------------------------------------------------------------
# Piper TTS (Linux amd64 binary)
# ---------------------------------------------------------------------------
PIPER_VERSION="2023.11.14-2"
PIPER_ARCHIVE="piper_linux_x86_64.tar.gz"
PIPER_URL="https://github.com/rhasspy/piper/releases/download/${PIPER_VERSION}/${PIPER_ARCHIVE}"
PIPER_INSTALL_DIR="${HOME}/piper"
PIPER_VOICE_MODEL="en_GB-vctk-medium"
PIPER_VOICE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_GB/vctk/medium/en_GB-vctk-medium.onnx"
PIPER_VOICE_JSON_URL="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_GB/vctk/medium/en_GB-vctk-medium.onnx.json"

install_piper() {
  info "Installing Piper TTS to ${PIPER_INSTALL_DIR}…"
  mkdir -p "${PIPER_INSTALL_DIR}/voices"

  TMP_DIR=$(mktemp -d)
  trap 'rm -rf "$TMP_DIR"' EXIT

  info "Downloading Piper binary (${PIPER_VERSION})…"
  wget -q --show-progress -O "${TMP_DIR}/${PIPER_ARCHIVE}" "${PIPER_URL}"
  tar -xzf "${TMP_DIR}/${PIPER_ARCHIVE}" -C "${TMP_DIR}"
  cp "${TMP_DIR}/piper/piper" "${PIPER_INSTALL_DIR}/piper"
  chmod +x "${PIPER_INSTALL_DIR}/piper"

  info "Downloading voice model (${PIPER_VOICE_MODEL})…"
  wget -q --show-progress -O "${PIPER_INSTALL_DIR}/voices/${PIPER_VOICE_MODEL}.onnx" "${PIPER_VOICE_URL}"
  wget -q --show-progress -O "${PIPER_INSTALL_DIR}/voices/${PIPER_VOICE_MODEL}.onnx.json" "${PIPER_VOICE_JSON_URL}"

  success "Piper TTS installed at ${PIPER_INSTALL_DIR}"
  success "Voice model: ${PIPER_INSTALL_DIR}/voices/${PIPER_VOICE_MODEL}.onnx"
}

# ---------------------------------------------------------------------------
# Python virtual environment + dependencies
# ---------------------------------------------------------------------------
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${REPO_ROOT}/.venv"

setup_python() {
  info "Creating Python virtual environment at ${VENV_DIR}…"
  python3 -m venv "${VENV_DIR}"
  # shellcheck disable=SC1091
  source "${VENV_DIR}/bin/activate"

  info "Upgrading pip…"
  pip install --quiet --upgrade pip

  info "Installing core Python dependencies…"
  pip install --quiet \
    fastapi uvicorn \
    python-socketio python-multipart \
    python-dotenv \
    flask flask-cors \
    aiohttp pillow \
    python-docx PyPDF2 \
    google-genai

  # Audio (best-effort — may require PortAudio headers)
  pip install --quiet pyaudio || warn "pyaudio install failed — voice input disabled. Install portaudio19-dev and retry."
  pip install --quiet SpeechRecognition || warn "SpeechRecognition install failed."

  if [ "${DEV_MODE}" = true ]; then
    info "Installing dev dependencies…"
    pip install --quiet pytest pytest-asyncio
  fi

  success "Python dependencies installed."
}

# ---------------------------------------------------------------------------
# .env file
# ---------------------------------------------------------------------------
setup_env() {
  if [ ! -f "${REPO_ROOT}/.env" ]; then
    info "Creating .env from template…"
    cp "${REPO_ROOT}/.env.template" "${REPO_ROOT}/.env"
    # Update Piper path to Linux default
    sed -i "s|PIPER_DIR=.*|PIPER_DIR=${PIPER_INSTALL_DIR}|" "${REPO_ROOT}/.env"
    success ".env created. Edit it to add your GEMINI_API_KEY."
  else
    info ".env already exists — skipping."
  fi
}

# ---------------------------------------------------------------------------
# systemd services
# ---------------------------------------------------------------------------
SYSTEMD_USER_DIR="${HOME}/.config/systemd/user"
SYSTEMD_SRC_DIR="${REPO_ROOT}/linux/systemd"

install_services() {
  info "Installing systemd user services…"
  mkdir -p "${SYSTEMD_USER_DIR}"

  for svc_template in "${SYSTEMD_SRC_DIR}"/*.service; do
    svc_name=$(basename "${svc_template}")
    # Substitute placeholders
    sed \
      -e "s|__REPO_ROOT__|${REPO_ROOT}|g" \
      -e "s|__VENV_DIR__|${VENV_DIR}|g" \
      -e "s|__USER__|${USER}|g" \
      "${svc_template}" > "${SYSTEMD_USER_DIR}/${svc_name}"
    info "  Installed: ${svc_name}"
  done

  systemctl --user daemon-reload
  success "systemd services installed. Enable with:"
  echo ""
  echo "    systemctl --user enable --now enki-api.service"
  echo "    systemctl --user enable --now enki-hud.service"
  echo "    systemctl --user enable --now enki-brain.service"
  echo "    systemctl --user enable --now enki-jarvis.service"
  echo ""
  echo "  To start without enabling on boot:"
  echo "    systemctl --user start enki-api.service"
}

# ---------------------------------------------------------------------------
# Data directory
# ---------------------------------------------------------------------------
setup_data_dir() {
  mkdir -p "${REPO_ROOT}/data"
  success "Data directory ready: ${REPO_ROOT}/data"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║    ENKI-AI  ·  Linux Install Script          ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════╝${NC}"
echo ""

install_system_deps
[ "${INSTALL_PIPER}" = true ] && install_piper
setup_python
setup_env
setup_data_dir
[ "${INSTALL_SYSTEMD}" = true ] && install_services

echo ""
success "Installation complete. OUSH. 🏺"
echo ""
echo "Next steps:"
echo "  1. Edit .env and set GEMINI_API_KEY"
echo "  2. Source the venv:  source ${VENV_DIR}/bin/activate"
echo "  3. Run the API:      python -m enki_ai.api.web_server"
echo "  4. Run the HUD:      python -m enki_ai.gui.hud_server"
echo "  5. Run JARVIS voice: python -m enki_ai.core.jarvis_core"
echo ""
