""""
    align-data-sorter.py

    Author: xokruc00
    Email: xokruc00@fit.vutbr.cz

    This script will copy all aligned .ctm files to the dataset and updates the dataset.json file.
    If an alignment file is missing it will print it to stdout.

    Input:
        -d / --dataset - path to dataset.json
        -a / --aligned-data - path to directory with .ctm files
        -c / --clips - path to directory with all clips

"""

import getopt
import json
import os
import shutil
import sys
from pathlib import Path

input_dir = ""
dataset = ""
clips = ""

def get_parameters():
    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, "ha:d:c:", ["aligned-data=", "dataset=", "clips="])
    except:
        print("Error")
        exit(1)

    for opt, arg in opts:
        if opt in ("-a", "--aligned-data"):
            global input_dir
            input_dir = arg
        elif opt in ("-d", "--dataset"):
            global dataset
            dataset = arg
        elif opt in ("-c", "--clips"):
            global clips
            clips = arg

def process_dataset(dataset, path, aligned_data, clips):
    index = 0
    for directory in dataset["data"]:
        if "prep-data-alignment" in directory:
            dataset["data"][index]["aligned-data"] = []
            for clip in directory["prep-data-alignment"]["mono"]:
                filename = clip["text"].split(".")[0] + ".ctm"
                if filename in aligned_data:
                    clips_path = clips + directory["dir-name"] + "/" + "aligned-data" + "/"
                    Path(clips_path).mkdir(parents=True, exist_ok=True)

                    source = path + filename
                    print(source, clips_path)
                    shutil.copy2(source, clips_path)

                    ctm_tmp = {}
                    ctm_tmp["ctm-file"] = filename
                    dataset["data"][index]["aligned-data"].append(ctm_tmp)
        index += 1
    return dataset



def is_ctm_file(file_name):
    if file_name.endswith(".ctm"):
        return True
    else:
        return False

def load_ctm_files(input_dir):
    command = "tree -J " + input_dir + " > ./tmp-aligned.json"
    os.popen(command).read()

    tree_file = open("./tmp-aligned.json", "r")

    with open("./tmp-aligned.json", "r") as file:
        raw_data = json.loads(file.read())

    aligned_data = {}
    for file in raw_data[0]["contents"]:
        if file["type"] == "file" and is_ctm_file(file["name"]):
            aligned_data[file["name"]] = True

    return aligned_data



get_parameters()

dataset_file = open(dataset, "r")
dataset_json = json.loads(dataset_file.read())
dataset_file.close()

aligned_data = load_ctm_files(input_dir)
new_dataset = process_dataset(dataset_json, input_dir, aligned_data, clips)

dataset_file = open(dataset, "w")
dataset_file.write(json.dumps(new_dataset, ensure_ascii=False))
dataset_file.close()


