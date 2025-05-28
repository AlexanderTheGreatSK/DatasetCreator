#!/bin/bash

PATH_TO_ARCHIVE=/run/media/alex/fd10f3e8-6e40-44bd-bf1b-3c72bf2e1900/BP24/dataset-reduced/clips/
DATASET_JSON=dataset.json
MANIFEST_FILE=manifest.json

# creates dataset.json from archive
python src/tree-2-json.py -i "$PATH_TO_ARCHIVE" -y

# text sanitize and cut the text and audio file
python src/text-sanitizer.py -d "$PATH_TO_ARCHIVE"

# this script creates manifests for NeMo Force Aligner
# you can use single manifest.json - in one manifests are all audio and text files
# this will align audio faster, but when error appears, it will stop alignment and you have to find the error
# alternatively you can use one manifest for one audio and text file, this will take more time but when error occurs it will continue alignment
python src/manifest-creator.py -d "$PATH_TO_ARCHIVE"

