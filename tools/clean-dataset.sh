#!/bin/bash

# this script will delete all new stuff created by the dataset pipeline

if [ -z "$1" ]; then
  echo "Usage: $0 <path>"
  exit 1
fi

TARGET_PATH="$1"

find "$TARGET_PATH" -type d -name 'prep-data-alignment' -exec rm -rf {} +
find "$TARGET_PATH" -type f -name '*stereo*' -exec rm -rf {} +
find "$TARGET_PATH" -type f -name '*mono*' -exec rm -rf {} +
find "$TARGET_PATH" -type d -name 'aligned-data' -exec rm -rf {} +
find "$TARGET_PATH" -type d -name 'training-data' -exec rm -rf {} +