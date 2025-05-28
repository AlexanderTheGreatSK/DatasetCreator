""""
    aligner-wrapper

    Author: xokruc00
    Email: xokruc00@fit.vutbr.cz

    This script serves as a wrapper for NeMo Force Aligner.
"""


!python3.12 /home/alex/Dokumenty/NeMo/tools/nemo_forced_aligner/align.py pretrained_name="stt_en_fastconformer_hybrid_large_pc" manifest_filepath=path_to_the_manifest output_dir=/home/alex/DataspellProjects/SpeechTextAlignment/create-manifest/totla-test/ save_output_file_formats=["ctm"]




# single manifest file version
#!python3.12 /home/alex/Dokumenty/NeMo/tools/nemo_forced_aligner/align.py pretrained_name="stt_en_fastconformer_hybrid_large_pc" manifest_filepath=/home/alex/Dokumenty/NeMo/tutorials/tools/jane-test/manifest.json output_dir=/home/alex/Dokumenty/NeMo/tutorials/tools/jane-test/nfa_output/

#multiple manifest files version
for i in range(0, 159):
    manifest_path = "/home/alex/DataspellProjects/SpeechTextAlignment/create-manifest/extra-new-manifest/manifest-" + str(i) + ".json"
    print("Doing ", str(i), "/155")
    !python3.12 /home/alex/Dokumenty/NeMo/tools/nemo_forced_aligner/align.py pretrained_name="stt_en_fastconformer_hybrid_large_pc" manifest_filepath="$manifest_path" output_dir=/home/alex/DataspellProjects/SpeechTextAlignment/create-manifest/test-out/ save_output_file_formats=["ctm"]
