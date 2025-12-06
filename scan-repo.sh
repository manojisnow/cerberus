#!/bin/bash
# Improved Docker run script with proper volume mounts for caches

REPO_PATH="${1:-/path/to/target-repo}"

echo "🐕 Running Cerberus Security Scanner"
echo "Repository: $REPO_PATH"
echo ""

# Create cache directories on host
mkdir -p $(pwd)/cache/trivy
mkdir -p $(pwd)/cache/semgrep
mkdir -p $(pwd)/cache/home

# Mount repository to same path in container to preserve paths in reports
docker run --rm \
  --tmpfs /tmp:rw,exec,size=4g \
  -v "$REPO_PATH:$REPO_PATH:ro" \
  -v $(pwd)/reports:/cerberus/reports \
  -v $(pwd)/cache/trivy:/home/cerberus/.cache/trivy \
  -v $(pwd)/cache/semgrep:/home/cerberus/.cache/semgrep \
  -v $(pwd)/cache/home:/home/cerberus/.cache \
  -e TRIVY_CACHE_DIR=/home/cerberus/.cache/trivy \
  cerberus:latest "$REPO_PATH"

echo ""
echo "✅ Scan complete! Reports in: $(pwd)/reports"
