#!/bin/bash
set -e
echo "🔄 Rolling back to v0.3.1..."

# Restore config files
if [ -f .chainlit/config.toml.backup ]; then
    cp .chainlit/config.toml.backup .chainlit/config.toml
    echo "✅ Config restored"
fi

# Restore project files
if [ -f pyproject.toml.backup ]; then
    cp pyproject.toml.backup pyproject.toml
    cp poetry.lock.backup poetry.lock
    echo "✅ Project files restored"
fi

# Restore dependencies
poetry install
echo "✅ Dependencies restored"

echo "✅ Rollback complete! Restart services with: docker compose restart"
