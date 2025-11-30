#!/bin/bash

PATH_TO_ARCHIVE=/mnt/matylda6/xokruc00/dataset/clips/
DATASET_JSON=/mnt/matylda6/xokruc00/dataset/dataset.json

# creates dataset.json from archive
python src/tree-2-json.py -i "$PATH_TO_ARCHIVE" -y

# text sanitize and cut the text and audio file
python src/text-sanitizer.py -d "$DATASET_JSON"

# this script creates manifests for NeMo Force Aligner
# you can use single manifest.json - in one manifests are all audio and text files
# this will align audio faster, but when error appears, it will stop alignment and you have to find the error
# alternatively you can use one manifest for one audio and text file, this will take more time but when error occurs it will continue alignment
python src/manifest-creator.py -d "$DATASET_JSON"

#TODO rewrite this nfa wrapper for your local installation of NFA and uncomment that line
#TODO match the output CTM directory in script
#sh src/nfa-wrapper.sh

CTM_FILES=/mnt/matylda6/xokruc00/dataset/clips/ctm/

# this script will pair CTM file with its audio file
python tools/align-data-sorter.py -d "$DATASET_JSON" -a "$CTM_FILES" -c "$PATH_TO_ARCHIVE"

# this script will create sub-30 seconds clips for training
TRAINING_TSV_PATH=/mnt/matylda6/xokruc00/dataset/
python src/clip-cutter.py -d "$DATASET_JSON" -o "$TRAINING_TSV_PATH"

