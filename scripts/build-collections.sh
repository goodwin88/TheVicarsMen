#!/usr/bin/env bash
set -e

MEGA_FILE="00-ALL-CONTENT.md"
echo "# Complete Content — All Collections" > "$MEGA_FILE"
echo "" >> "$MEGA_FILE"
echo "> ⚠️ This file is auto-generated. Edit the individual files in each collection instead." >> "$MEGA_FILE"
echo "" >> "$MEGA_FILE"

# Loop over each numbered directory in order
for DIR in $(ls -d [0-9][0-9]-*/ | sort); do
  DIR=${DIR%/}  # remove trailing slash
  COLLECTION_NUM=$(basename "$DIR" | cut -d'-' -f1)
  COLLECTION_NAME=$(basename "$DIR" | cut -d'-' -f2)
  COLLECTION_HEADER="${COLLECTION_NAME^}" # Capitalize first letter

  # Per-collection compiled file
  OUT="$DIR/00-ALL-${COLLECTION_NAME^^}.md" # all caps for filename

  echo "# ${COLLECTION_HEADER} — Complete Text" > "$OUT"
  echo "" >> "$OUT"
  echo "> ⚠️ This file is auto-generated. Edit the individual files instead." >> "$OUT"
  echo "" >> "$OUT"

  # Loop over numbered markdown files in order
  for FILE in $(ls "$DIR"/[0-9][0-9]-*.md 2>/dev/null | sort); do
    # Skip output file itself
    [[ "$FILE" == "$OUT" ]] && continue

    FILE_NAME=$(basename "$FILE" .md)
    STORY_TITLE=$(echo "$FILE_NAME" | cut -d'-' -f2- | sed -E 's/-/ /g')
    
    # Add story header in per-collection file
    echo "" >> "$OUT"
    echo "## ${STORY_TITLE^}" >> "$OUT"
    echo "" >> "$OUT"
    cat "$FILE" >> "$OUT"
  done

  echo "Compiled collection file: $OUT"

  # Add to mega file with clear collection header
  echo "" >> "$MEGA_FILE"
  echo "## Collection: ${COLLECTION_HEADER}" >> "$MEGA_FILE"
  echo "" >> "$MEGA_FILE"
  cat "$OUT" >> "$MEGA_FILE"
  echo "" >> "$MEGA_FILE"
done

echo "Compiled mega file: $MEGA_FILE"
