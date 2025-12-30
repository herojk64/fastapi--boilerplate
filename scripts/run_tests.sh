#!/usr/bin/env bash
set -euo pipefail

# Convenience script to run the test suite using Poetry.
# Usage: ./scripts/run_tests.sh [pytest-args]

if ! command -v poetry >/dev/null 2>&1; then
  echo "poetry is required. Install it or run tests with your environment's pytest."
  exit 1
fi

ARGS=${*:-}
poetry run pytest ${ARGS}
