#!/bin/bash
#
# Dashboard Scraper Cron Wrapper
#
# This script provides a robust wrapper for running the dashboard scraper
# from cron with proper error handling, logging, and notifications.
#
# Usage:
#   ./scripts/run_scraper.sh
#
# Cron example (daily at 1:05 AM UTC):
#   5 1 * * * /opt/dashboard-scraper/scripts/run_scraper.sh
#

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"
PYTHON="$VENV_PATH/bin/python"
LOG_DIR="${LOG_DIR:-/var/log}"
LOG_FILE="$LOG_DIR/dashboard_scraper.log"
ERROR_LOG="$LOG_DIR/dashboard_scraper_error.log"

# Optional: Slack webhook for notifications
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"

# Logging functions
log() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] $*" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] ERROR: $*" | tee -a "$LOG_FILE" "$ERROR_LOG" >&2
}

notify_slack() {
    local message="$1"
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"$message\"}" \
            "$SLACK_WEBHOOK_URL" 2>/dev/null || true
    fi
}

# Preflight checks
if [ ! -d "$VENV_PATH" ]; then
    log_error "Virtual environment not found at $VENV_PATH"
    notify_slack "❌ Dashboard scraper failed: venv not found"
    exit 1
fi

if [ ! -f "$PYTHON" ]; then
    log_error "Python interpreter not found at $PYTHON"
    notify_slack "❌ Dashboard scraper failed: Python not found"
    exit 1
fi

if [ ! -f "$PROJECT_ROOT/.env" ]; then
    log_error ".env file not found at $PROJECT_ROOT/.env"
    notify_slack "❌ Dashboard scraper failed: .env missing"
    exit 1
fi

# Change to project directory
cd "$PROJECT_ROOT"

# Run the scraper
log "Starting dashboard scraper"
START_TIME=$(date +%s)

if OUTPUT=$("$PYTHON" -m dashboard_scraper 2>&1); then
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    # Extract output file path from stdout (last line)
    OUTPUT_FILE=$(echo "$OUTPUT" | tail -n 1)
    
    if [ -f "$OUTPUT_FILE" ]; then
        FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
        ROW_COUNT=$(($(wc -l < "$OUTPUT_FILE") - 1))  # Subtract header
        
        log "✓ Scraper completed successfully in ${DURATION}s"
        log "  Output: $OUTPUT_FILE"
        log "  Size: $FILE_SIZE"
        log "  Rows: $ROW_COUNT"
        
        notify_slack "✅ Dashboard scraper completed: $ROW_COUNT rows, $FILE_SIZE, ${DURATION}s"
    else
        log "✓ Scraper completed in ${DURATION}s (no output file detected)"
    fi
    
    exit 0
else
    EXIT_CODE=$?
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    
    log_error "Scraper failed with exit code $EXIT_CODE after ${DURATION}s"
    log_error "Output:"
    echo "$OUTPUT" | tee -a "$ERROR_LOG"
    
    notify_slack "❌ Dashboard scraper failed (exit $EXIT_CODE) after ${DURATION}s"
    
    exit $EXIT_CODE
fi

