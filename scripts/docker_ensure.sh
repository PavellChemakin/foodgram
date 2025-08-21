set -euo pipefail

USER_HOME="$HOME"
CFG_DIR="$USER_HOME/.config/foodgram"
ENV_FILE="$CFG_DIR/env"
mkdir -p "$CFG_DIR"
mkdir -p "$USER_HOME/foodgram"

use_system_docker() {
  if command -v sudo >/dev/null 2>&1; then
    sudo systemctl enable docker.service docker.socket >/dev/null 2>&1 || true
    sudo systemctl start docker.service >/dev/null 2>&1 || true
    for i in $(seq 1 30); do
      if sudo docker info >/dev/null 2>&1; then
        printf "USE_SUDO=1\nDOCKER_HOST=\n" > "$ENV_FILE"
        return 0
      fi
      sleep 1
    done
  fi
  return 1
}

use_rootless_docker() {
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update -y
    sudo apt-get install -y docker-ce-rootless-extras uidmap dbus-user-session fuse-overlayfs
  fi
  export XDG_RUNTIME_DIR="/run/user/$(id -u)"
  mkdir -p "$XDG_RUNTIME_DIR"
  if ! command -v dockerd-rootless-setuptool.sh >/dev/null 2>&1; then
    return 1
  fi
  if [ ! -S "$XDG_RUNTIME_DIR/docker.sock" ]; then
    dockerd-rootless-setuptool.sh install || true
  fi
  loginctl enable-linger "$(whoami)" >/dev/null 2>&1 || true
  systemctl --user daemon-reload >/dev/null 2>&1 || true
  systemctl --user enable --now docker >/dev/null 2>&1 || true
  export DOCKER_HOST="unix:///run/user/$(id -u)/docker.sock"
  for i in $(seq 1 60); do
    if docker info >/dev/null 2>&1; then
      printf "USE_SUDO=0\nDOCKER_HOST=%s\n" "$DOCKER_HOST" > "$ENV_FILE"
      return 0
    fi
    sleep 1
  done
  return 1
}

if use_system_docker; then
  exit 0
fi

if use_rootless_docker; then
  exit 0
fi

echo "Docker daemon is not available (system and rootless both failed)." >&2
exit 1
