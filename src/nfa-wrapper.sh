#!/bin/bash

conda activate nemo

python /home/alex/Documents/NeMo/tools/nemo_forced_aligner/align.py pretrained_name="stt_en_fastconformer_hybrid_large_pc" manifest_filepath=/home/alex/DataspellProjects/DatasetCreator/src/manifests/manifest-0.json output_dir=/home/alex/Documents/nfa-out save_output_file_formats=["ctm"]