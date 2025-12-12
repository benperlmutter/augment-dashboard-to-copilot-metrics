#!/bin/bash
#
# Setup Cron Job for Dashboard Scraper
#
# This script helps configure a cron job for the dashboard scraper.
# It validates the setup and adds the cron entry.
#
# Usage:
#   sudo ./scripts/setup_cron.sh [cron_schedule]
#
# Example:
#   sudo ./scripts/setup_cron.sh "5 1 * * *"  # Daily at 1:05 AM UTC
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RUN_SCRIPT="$SCRIPT_DIR/run_scraper.sh"

# Default schedule: daily at 1:05 AM UTC
CRON_SCHEDULE="${1:-5 1 * * *}"

echo "Dashboard Scraper Cron Setup"
echo "============================="
echo ""
echo "Project root: $PROJECT_ROOT"
echo "Run script: $RUN_SCRIPT"
echo "Schedule: $CRON_SCHEDULE"
echo ""

# Validate setup
echo "Validating setup..."

if [ ! -f "$RUN_SCRIPT" ]; then
    echo "ERROR: Run script not found at $RUN_SCRIPT"
    exit 1
fi

if [ ! -x "$RUN_SCRIPT" ]; then
    echo "Making run script executable..."
    chmod +x "$RUN_SCRIPT"
fi

if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "ERROR: Virtual environment not found. Run 'python -m venv .venv' first."
    exit 1
fi

if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "WARNING: .env file not found. Make sure to create it before running."
fi

if [ ! -f "$PROJECT_ROOT/secrets/tokens.json" ]; then
    echo "WARNING: OAuth tokens not found. Run 'python -m dashboard_scraper --auth' first."
fi

echo "✓ Setup validation passed"
echo ""

# Generate cron entry
CRON_ENTRY="$CRON_SCHEDULE $RUN_SCRIPT"

echo "Cron entry to add:"
echo "  $CRON_ENTRY"
echo ""

# Check if entry already exists
if crontab -l 2>/dev/null | grep -F "$RUN_SCRIPT" >/dev/null; then
    echo "WARNING: A cron entry for this script already exists:"
    crontab -l | grep -F "$RUN_SCRIPT"
    echo ""
    read -p "Remove existing entry and add new one? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove existing entry
        crontab -l | grep -v -F "$RUN_SCRIPT" | crontab -
        echo "✓ Removed existing entry"
    else
        echo "Aborted."
        exit 0
    fi
fi

# Add cron entry
read -p "Add this cron entry? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
    echo "✓ Cron entry added successfully"
    echo ""
    echo "Current crontab:"
    crontab -l
else
    echo "Aborted."
    exit 0
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Ensure .env is configured: $PROJECT_ROOT/.env"
echo "  2. Authenticate once: cd $PROJECT_ROOT && python -m dashboard_scraper --auth"
echo "  3. Test the cron script: $RUN_SCRIPT"
echo "  4. Monitor logs: tail -f /var/log/dashboard_scraper.log"

