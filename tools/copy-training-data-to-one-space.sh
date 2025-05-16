#!/bin/bash

# this script copies all training data to one directory

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <search_path> <destination_path>"
  exit 1
fi

SEARCH_PATH="$1"
DEST_PATH="$2"

# if destination does not exist, creates it
mkdir -p "$DEST_PATH"

find "$SEARCH_PATH" -type d -name "training-data" -exec bash -c '
  for dir; do
    echo "Copying from: $dir to: '"$DEST_PATH"'"
    cp -r "$dir"/* '"$DEST_PATH"'
  done
' bash {} +
