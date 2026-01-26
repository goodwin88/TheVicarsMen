#!/usr/bin/env bash
# Robustly compile per-collection files and a single mega file.
set -euo pipefail
IFS=$'\n\t'

# Allow globs that don't match to expand to nothing
shopt -s nullglob

MEGA_FILE="00-ALL-CONTENT.md"

printf '%s\n\n' "# Complete Content — All Collections" > "$MEGA_FILE"
printf '%s\n\n' "> ⚠️ This file is auto-generated. Edit the individual files in each collection instead." >> "$MEGA_FILE"

# Collect collection directories matching NN-name/ and sort deterministically
mapfile -t DIRS < <(printf '%s\n' [0-9][0-9]-*/ | sort)

if [ "${#DIRS[@]}" -eq 0 ]; then
  echo "No collection directories found; nothing to compile."
  exit 0
fi

for DIR_PATH in "${DIRS[@]}"; do
  # Remove trailing slash
  DIR="${DIR_PATH%/}"

  # Extract leading number and the rest of the name (preserve hyphens in name)
  COLLECTION_NUM="${DIR%%-*}"
  COLLECTION_NAME="${DIR#*-}"
  COLLECTION_HEADER="${COLLECTION_NAME^}"  # capitalize first char

  # Per-collection compiled file
  OUT="$DIR/00-ALL-${COLLECTION_NAME^^}.md"

  {
    printf '%s\n\n' "# ${COLLECTION_HEADER} — Complete Text"
    printf '%s\n\n' "> ⚠️ This file is auto-generated. Edit the individual files instead."
  } > "$OUT"

  # Gather files matching NN-*.md or NN.x-*.md inside this collection dir (sorted)
  # NOTE: changed glob to [0-9][0-9]*-*.md to include subsection filenames like 08.1-*.md
  mapfile -t FILES < <(printf '%s\n' "$DIR"/[0-9][0-9]*-*.md | sort)

  for FILE in "${FILES[@]:-}"; do
    # Skip if glob produced pattern (no match) or file doesn't exist
    [ -e "$FILE" ] || continue

    # Skip the output file itself if it happens to match the pattern
    [ "$FILE" = "$OUT" ] && continue

    FILE_NAME=$(basename "$FILE" .md)

    # If filename has a dash separator, remove the leading number and first dash.
    # If not, use the full filename as title
    if [[ "$FILE_NAME" == *-* ]]; then
      STORY_TITLE="${FILE_NAME#*-}"
    else
      STORY_TITLE="$FILE_NAME"
    fi

    # Replace remaining dashes with spaces for the title
    STORY_TITLE="${STORY_TITLE//-/ }"

    {
      printf '\n%s\n\n' "## ${STORY_TITLE^}"
      # Preserve file contents; read safely
      cat -- "$FILE"
    } >> "$OUT"
  done

  echo "Compiled collection file: $OUT"

  # Add to mega file with clear collection header, but include only the collection contents
  {
    printf '\n%s\n\n' "## Collection: ${COLLECTION_HEADER}"
    cat -- "$OUT"
    printf '\n'
  } >> "$MEGA_FILE"
done

echo "Compiled mega file: $MEGA_FILE"