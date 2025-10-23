#!/bin/bash

# Building API Runner Setup Script
# Bu script serverda building-api uchun GitHub Actions runner sozlaydi

set -e

echo "🤖 =============================================="
echo "🤖 BUILDING API RUNNER SETUP"
echo "🤖 =============================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root"
    echo "Usage: sudo $0"
    exit 1
fi

# Set runner directory
RUNNER_DIR="/var/www/building-api/runner"
RUNNER_VERSION="2.311.0"

echo "📁 Runner directory: $RUNNER_DIR"

# Create runner directory
echo "📁 Creating runner directory..."
mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

# Download runner
echo "📥 Downloading GitHub Actions runner..."
curl -o actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz -L https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

# Extract runner
echo "📦 Extracting runner files..."
tar xzf ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz
rm ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

# Set permissions
echo "🔐 Setting permissions..."
chown -R root:root "$RUNNER_DIR"
chmod +x "$RUNNER_DIR/config.sh"
chmod +x "$RUNNER_DIR/run.sh"
chmod +x "$RUNNER_DIR/svc.sh"

echo ""
echo "✅ =============================================="
echo "✅ RUNNER DOWNLOADED SUCCESSFULLY!"
echo "✅ =============================================="
echo ""
echo "📋 Next Steps:"
echo "1. Go to GitHub: https://github.com/a-d-sh/building/settings/actions/runners"
echo "2. Click 'New self-hosted runner'"
echo "3. Copy the setup commands and run:"
echo ""
echo "   cd $RUNNER_DIR"
echo "   ./config.sh --url https://github.com/a-d-sh/building --token YOUR_TOKEN"
echo "   ./svc.sh install"
echo "   ./svc.sh start"
echo ""
echo "🔗 GitHub Repository: https://github.com/a-d-sh/building"
echo "🔗 Runner Settings: https://github.com/a-d-sh/building/settings/actions/runners"
echo ""
echo "📊 After setup, check runner status:"
echo "   systemctl status actions.runner.building-api"
echo "   journalctl -u actions.runner.building-api -f"
echo ""
echo "🎉 Runner setup completed! Follow the next steps above."
