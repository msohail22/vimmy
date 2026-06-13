#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "=== lint-web ==="
bun run lint 2>&1
echo ""

echo "=== build-web ==="
bun run build 2>&1
echo ""

echo "=== test-shared ==="
bun run test 2>&1
echo ""

echo "=== typecheck-api ==="
bun run typecheck 2>&1
echo ""

echo "=== build-api ==="
bun run build 2>&1
echo ""

echo "=== All checks passed ==="
