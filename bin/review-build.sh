#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PY:-/opt/homebrew/bin/python3.12}"
WB="$ROOT/.tools/reviewable-html-workbench"

usage() {
  cat <<'EOF'
Usage:
  bin/review-build.sh <name> <source-md> [--title TITLE] [--document-id ID]
  bin/review-build.sh preview <name>
  bin/review-build.sh ingest <name>

Examples:
  bin/review-build.sh CSW61_architecture_v3 会議設計/CSW61_architecture_v3.md \
    --title "CSW61 模擬国連会議設計まとめ v3" --document-id csw61-architecture-v3
  bin/review-build.sh preview CSW61_architecture_v3
  bin/review-build.sh ingest CSW61_architecture_v3
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

cmd="$1"
shift

case "$cmd" in
  preview)
    name="${1:?name required}"
    cd "$WB"
    exec "$PY" -m scripts.html_review_workbench.cli preview \
      --root "$ROOT/reviews/$name/bundle" --mode local
    ;;
  ingest)
    name="${1:?name required}"
    cd "$WB"
    exec "$PY" -m scripts.html_review_workbench.cli ingest-review \
      --root "$ROOT/reviews/$name/bundle"
    ;;
  *)
    name="$cmd"
    src_rel="${1:?source md required}"
    shift
    title=""
    document_id=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --title) title="$2"; shift 2 ;;
        --document-id) document_id="$2"; shift 2 ;;
        *) echo "Unknown arg: $1" >&2; exit 1 ;;
      esac
    done
    src="$ROOT/$src_rel"
    out="$ROOT/reviews/$name"
    title="${title:-$name}"
    document_id="${document_id:-$(echo "$name" | tr '[:upper:]' '[:lower:]' | tr '_' '-')}"

    "$PY" "$ROOT/reviews/scripts/md_to_document_model.py" \
      --input "$src" \
      --output "$out/document-model.json" \
      --title "$title" \
      --document-id "$document_id"

    cd "$WB"
    "$PY" -m scripts.html_review_workbench.cli check-model --model "$out/document-model.json"
    "$PY" -m scripts.html_review_workbench.cli render --model "$out/document-model.json" --output "$out/bundle"
    "$PY" -m scripts.html_review_workbench.cli validate --root "$out/bundle"
    echo "Built: $out/bundle/index.html"
    ;;
esac
