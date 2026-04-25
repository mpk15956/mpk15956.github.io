#!/usr/bin/env bash
# Rebuild favicon + OG card from _assets/ SVG sources.
# Run this when you edit either SVG. Built artifacts are tracked in git
# so the GitHub Action doesn't need Inkscape/ImageMagick installed.

set -euo pipefail
cd "$(dirname "$0")/.."

# Favicon: SVG passthrough + PNG sizes + multi-resolution ICO.
cp _assets/favicon.svg favicon.svg
inkscape _assets/favicon.svg --export-type=png --export-width=16  -o favicon-16.png  >/dev/null
inkscape _assets/favicon.svg --export-type=png --export-width=32  -o favicon-32.png  >/dev/null
inkscape _assets/favicon.svg --export-type=png --export-width=48  -o favicon-48.png  >/dev/null
inkscape _assets/favicon.svg --export-type=png --export-width=180 -o apple-touch-icon.png >/dev/null
magick favicon-16.png favicon-32.png favicon-48.png favicon.ico
rm favicon-16.png favicon-32.png favicon-48.png

# OG card: 1200x630 PNG.
inkscape _assets/og-card.svg --export-type=png --export-width=1200 -o og-card.png >/dev/null

echo "Built: favicon.svg favicon.ico apple-touch-icon.png og-card.png"
