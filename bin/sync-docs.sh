#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DOCS="$ROOT/docs"
SRC="$ROOT/会議設計"

files=(
  CSW61_architecture_v2.md
  CSW61_architecture_v3.md
  CSW61_country_matrix_v3.html
  CSW61_country_stance_matrix.html
  CSW61_final_agreement_draft.md
)

for f in "${files[@]}"; do
  cp "$SRC/$f" "$DOCS/$f"
  echo "synced: $f"
done

echo "Done. Commit docs/ when ready for GitHub Pages."
