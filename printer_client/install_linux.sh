#!/bin/bash
set -e

# Must be run as root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Run as root: sudo bash install_linux.sh"
    exit 1
fi

INSTALL_DIR=/opt/arabica-printer
SERVICE_NAME=arabica-printer
SERVICE_USER=arabica-printer
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Arabica Print Client — Linux Install ==="

have_python_deps() {
    command -v python3 >/dev/null 2>&1 &&
    python3 -m venv --help >/dev/null 2>&1 &&
    python3 -m pip --version >/dev/null 2>&1
}

# Create system user (no login, no home)
if ! id "$SERVICE_USER" &>/dev/null; then
    echo "Creating user $SERVICE_USER..."
    useradd --system --no-create-home --shell /usr/sbin/nologin "$SERVICE_USER"
fi

# Install Python deps
if [ "${SKIP_APT:-0}" = "1" ]; then
    echo "SKIP_APT=1 set; skipping apt packages."
    if ! have_python_deps; then
        echo "ERROR: python3, python3-venv or python3-pip is missing."
        exit 1
    fi
elif have_python_deps; then
    echo "Python, venv and pip are already installed; skipping apt packages."
else
    echo "Installing system packages..."
    if ! apt-get update -qq; then
        echo ""
        echo "ERROR: apt-get update failed."
        echo "Fix disabled/expired apt repositories, or install these packages manually:"
        echo "  sudo apt-get install -y python3 python3-venv python3-pip --no-install-recommends"
        echo ""
        echo "If Python, venv and pip are already available, re-run with:"
        echo "  SKIP_APT=1 sudo -E bash install_linux.sh"
        exit 1
    fi
    apt-get install -y python3 python3-venv python3-pip --no-install-recommends
fi

# Create install directory
echo "Copying files to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR/logs"
cp "$SCRIPT_DIR/client.py"   "$INSTALL_DIR/"
cp "$SCRIPT_DIR/printer.py"  "$INSTALL_DIR/"
cp "$SCRIPT_DIR/config.json" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"

# Create virtualenv and install deps
echo "Installing Python dependencies..."
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip -q
"$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt" -q

# Set permissions
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
chmod 750 "$INSTALL_DIR"
chmod 640 "$INSTALL_DIR/config.json"

# Install systemd service
echo "Installing systemd service..."
cp "$SCRIPT_DIR/arabica-printer.service" /etc/systemd/system/

# Update WorkingDirectory and ExecStart in service file
sed -i "s|/opt/arabica-printer|$INSTALL_DIR|g" /etc/systemd/system/arabica-printer.service
sed -i "s|User=arabica-printer|User=$SERVICE_USER|g" /etc/systemd/system/arabica-printer.service

# Enable and start
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

echo ""
echo "=== Installation complete ==="
echo "Status:  systemctl status $SERVICE_NAME"
echo "Logs:    journalctl -u $SERVICE_NAME -f"
echo "Stop:    systemctl stop $SERVICE_NAME"
echo "Config:  nano $INSTALL_DIR/config.json"
