#!/usr/bin/env bash
set -e

MEGA_FILE="00-ALL-CONTENT.md"
echo "# Complete Content — All Collections" > "$MEGA_FILE"
echo "" >> "$MEGA_FILE"
echo "> ⚠️ This file is auto-generated. Edit the individual files in each collection instead." >> "$MEGA_FILE"
echo "" >> "$MEGA_FILE"

# Loop over each numbered directory at the root
for DIR in [0-9][0-9]-*/; do
  DIR=${DIR%/}  # remove trailing slash
  COLLECTION_NAME=$(basename "$DIR" | cut -d'-' -f2) # e.g., fairy-tales
  OUT="$DIR/00-ALL-${COLLECTION_NAME^^}.md" # per-collection file

  echo "# ${COLLECTION_NAME^} — Complete Text" > "$OUT"
  echo "" >> "$OUT"
  echo "> ⚠️ This file is auto-generated. Edit the individual files instead." >> "$OUT"
  echo "" >> "$OUT"

  # Loop over numbered .md files inside, sorted
  for FILE in "$DIR"/[0-9][0-9]-*.md; do
    # Skip the output file if it exists from previous runs
    [[ "$FILE" == "$OUT" ]] && continue

    echo "" >> "$OUT"
    echo "---" >> "$OUT"
    echo "" >> "$OUT"
    cat "$FILE" >> "$OUT"
  done

  echo "Compiled $OUT"

  # Append this collection to mega file
  echo "" >> "$MEGA_FILE"
  echo "## ${COLLECTION_NAME^} Collection" >> "$MEGA_FILE"
  echo "" >> "$MEGA_FILE"
  cat "$OUT" >> "$MEGA_FILE"
  echo "" >> "$MEGA_FILE"
done

echo "Compiled mega file: $MEGA_FILE"
