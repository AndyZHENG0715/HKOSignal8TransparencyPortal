#!/bin/sh
# Package only public website assets; use the committed JSON snapshot unchanged.
set -eu
cd "$(dirname "$0")/.."
mkdir -p dist/prototypes dist/data/events dist/assets
cp prototypes/charts.html dist/index.html
cp prototypes/charts.html dist/prototypes/charts.html
cp data/index.json dist/data/index.json
cp data/events/*.json dist/data/events/
cp public/favicon.svg dist/assets/favicon.svg
cp public/social-preview.png dist/assets/social-preview.png
