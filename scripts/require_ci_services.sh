#!/usr/bin/env bash
# In CI, fail unless both test servers are configured. The server tests skip when their
# setting is absent, which is right on a laptop; in CI a skip would hide a removed
# service, so scripts/check.sh runs this first.
set -euo pipefail
if [ -n "${CI:-}" ]; then
  : "${LIONG_SQLSERVER:?CI must set LIONG_SQLSERVER}" "${LIONG_NEO4J:?CI must set LIONG_NEO4J}"
fi
