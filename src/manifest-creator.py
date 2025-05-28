"""
    manifest-creator.py

    Author: xokruc00
    Email: xokruc00@fit.vutbr.cz

    This script creates manifest files for a NeMo Force Aligner from the dataset.json file.

    Input:
        -d / --dataset - path to dataset.json
"""


import getopt
import json
import sys


def get_parameters():
    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, "hd:", ["dataset="])
    except:
        print("Error")
        exit(1)

    for opt, arg in opts:
        if opt in ("-d", "--dataset"):
            global input_file
            input_file = arg

get_parameters()
file = open(input_file, "r")

json_data = json.load(file)

manifest = ""
path = json_data["path"]

index = 0

for item in json_data["data"]:
    dir = item["dir-name"] + "/"
    if "prep-data-alignment" in item:
        if "mono" in item["prep-data-alignment"]:
            for mono_clip in item["prep-data-alignment"]["mono"]:
                current_path = path + dir + "prep-data-alignment/mono/"
                tmp = {}
                tmp["audio_filepath"] = current_path + mono_clip["audio"]

                with open(current_path + mono_clip["text"], "r", encoding="utf-8") as txt_file:
                    tmp["text"] = txt_file.readline()

                name = "./manifest-" + str(index) + ".json"
                index += 1

                tmp_manifest = json.dumps(tmp, ensure_ascii=False) + "\n"

                file_out = open(name, "w", encoding='utf-8')
                file_out.write(tmp_manifest)
                file_out.close()

                manifest += json.dumps(tmp, ensure_ascii=False) + "\n"

file.close()
file_out = open("manifests/manifest.json", "w", encoding='utf-8')
file_out.write(manifest)
file_out.close()