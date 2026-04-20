#!/usr/bin/env bash
# =============================================================================
# Enki-AI — systemd service manager helper
# =============================================================================
# Installs, removes, starts, stops, or shows status of all Enki services.
#
# Usage:
#   ./linux/systemd/manage-services.sh install [REPO_ROOT] [VENV_DIR]
#   ./linux/systemd/manage-services.sh remove
#   ./linux/systemd/manage-services.sh start
#   ./linux/systemd/manage-services.sh stop
#   ./linux/systemd/manage-services.sh status
#   ./linux/systemd/manage-services.sh logs <service>
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${2:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
VENV_DIR="${3:-${REPO_ROOT}/.venv}"
SYSTEMD_USER_DIR="${HOME}/.config/systemd/user"

SERVICES=(enki-api enki-hud enki-brain enki-jarvis)

GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'

info()    { echo -e "${CYAN}[ENKI]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }

cmd="${1:-status}"

case "$cmd" in
  install)
    info "Installing Enki systemd services to ${SYSTEMD_USER_DIR}…"
    mkdir -p "${SYSTEMD_USER_DIR}"
    for svc in "${SERVICES[@]}"; do
      sed \
        -e "s|__REPO_ROOT__|${REPO_ROOT}|g" \
        -e "s|__VENV_DIR__|${VENV_DIR}|g" \
        -e "s|__USER__|${USER}|g" \
        "${SCRIPT_DIR}/${svc}.service" > "${SYSTEMD_USER_DIR}/${svc}.service"
      info "  Installed: ${svc}.service"
    done
    systemctl --user daemon-reload
    success "All services installed. Run: ./manage-services.sh start"
    ;;

  remove)
    info "Removing Enki systemd services…"
    for svc in "${SERVICES[@]}"; do
      systemctl --user stop "${svc}.service"   2>/dev/null || true
      systemctl --user disable "${svc}.service" 2>/dev/null || true
      rm -f "${SYSTEMD_USER_DIR}/${svc}.service"
      info "  Removed: ${svc}.service"
    done
    systemctl --user daemon-reload
    success "All services removed."
    ;;

  start)
    info "Starting all Enki services…"
    for svc in "${SERVICES[@]}"; do
      systemctl --user start "${svc}.service" && info "  Started: ${svc}" || true
    done
    ;;

  stop)
    info "Stopping all Enki services…"
    for svc in "${SERVICES[@]}"; do
      systemctl --user stop "${svc}.service" && info "  Stopped: ${svc}" || true
    done
    ;;

  enable)
    info "Enabling all Enki services (start on login)…"
    for svc in "${SERVICES[@]}"; do
      systemctl --user enable "${svc}.service" && info "  Enabled: ${svc}" || true
    done
    ;;

  disable)
    info "Disabling all Enki services…"
    for svc in "${SERVICES[@]}"; do
      systemctl --user disable "${svc}.service" && info "  Disabled: ${svc}" || true
    done
    ;;

  status)
    for svc in "${SERVICES[@]}"; do
      echo -e "${CYAN}── ${svc} ──────────────────────────────${NC}"
      systemctl --user status "${svc}.service" --no-pager 2>/dev/null || echo "  (not installed)"
    done
    ;;

  logs)
    svc="${2:-enki-api}"
    journalctl --user -u "${svc}.service" -f
    ;;

  *)
    echo "Usage: $0 {install|remove|start|stop|enable|disable|status|logs <svc>}"
    exit 1
    ;;
esac
