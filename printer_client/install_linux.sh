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

# Create system user (no login, no home)
if ! id "$SERVICE_USER" &>/dev/null; then
    echo "Creating user $SERVICE_USER..."
    useradd --system --no-create-home --shell /usr/sbin/nologin "$SERVICE_USER"
fi

# Install Python deps
echo "Installing system packages..."
apt-get update -qq
apt-get install -y python3 python3-venv python3-pip --no-install-recommends

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
