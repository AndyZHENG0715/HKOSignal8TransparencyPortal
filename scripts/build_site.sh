#!/bin/sh
# Deploy committed public output only. Data regeneration is an intentional local step.
set -eu
cd "$(dirname "$0")/.."
mkdir -p dist/prototypes dist/data/events dist/assets
cp -R website/. dist/
cp prototypes/charts.html dist/prototypes/charts.html
# Legacy chart keeps its original data contract under /data/index.json and /data/events.
# New portal uses /data/summary.json and /data/events-v2 to avoid mixing schemas.
cp data/index.json dist/data/index.json
cp data/events/*.json dist/data/events/
cp public/favicon.svg dist/assets/favicon.svg
cp public/social-preview.png dist/assets/social-preview.png
