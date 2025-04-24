import sys
import getopt
import json
from pathlib import Path

import pydub
import csv

# Inputs:
# input json file with audio and ctm
# output directory

dataset_file = None
output_path = None
tsv_header = ['audio', 'sentence', 'length']
mono_tsv_row = []
stereo_tsv_row = []
stereo = False

def get_parameters():
    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, "hd:o:s", ["dataset=", "output=", "stereo"])
    except:
        print("Error")
        exit(1)

    for opt, arg in opts:
        if opt in ("-d", "--dataset"):
            global dataset_file
            dataset_file = arg
        elif opt in ("-o", "--output"):
            global output_path
            output_path = arg
        elif opt in ("-s", "--stereo"):
            global stereo
            stereo = True

    print(dataset_file)
    print(output_path)


def write_to_tsv():
    global tsv_header
    global mono_tsv_row
    global stereo_tsv_row
    global output_path

    print(output_path)
    mono_out = output_path + "mono_output.tsv"
    stereo_out = output_path + "mono_output.tsv"

    with open(mono_out, "w") as tsv_file:
        writer = csv.writer(tsv_file, delimiter="\t")
        writer.writerow(tsv_header)
        writer.writerows(mono_tsv_row)
        tsv_file.close()

def cut_audio(path, name, audio, start, end):
    print("Cutting audio")
    print("Start:", start)
    print("End:", end)

    out = path + "/" + name

    segment = audio[start*1000:end*1000]
    segment.export(out, format="wav")


def compute_cuts(ctm_file, max_segment_length, mono_audio, stereo_audio, output_dir, filename):
    text = ""
    time = 0.0
    segment_dynamic_length = float(max_segment_length)
    global mono_tsv_row
    global stereo_tsv_row

    new_segment = True
    segment_counter = 1
    clip_name = ""
    segment_start = 0.0
    final_out_path = "/mnt/matylda6/xokruc00/training-data/mono/"

    for line in ctm_file:
        line_list = line.split()

        if clip_name == "":
            clip_name = line_list[0]

        if new_segment:
            new_segment = False

        word_end = float(line_list[2]) + float(line_list[3])
        if word_end > segment_dynamic_length:

            new_mono_name = filename + "_m" + str(segment_counter) + ".wav"
            new_stereo_name = filename + "_s" + str(segment_counter) + ".wav"
            clip_len = time - float(segment_start)

            mono_tsv_row.append([final_out_path + new_mono_name, text, round(clip_len,2)])

            cut_audio(output_dir + "mono/", new_mono_name, mono_audio, round(float(segment_start),2), round(float(time),2))

            new_segment = True
            segment_counter += 1
            time = float(line_list[2])
            text = line_list[4]
            segment_start = line_list[2]
            segment_dynamic_length += float(max_segment_length)
        else:
            if text == "":
                text = text + line_list[4]
            else:
                text = text + " " + line_list[4]

            time = float(word_end)

    if text != "":
        new_mono_name = filename + "_m" + str(segment_counter) + ".wav"
        clip_len = time - float(segment_start)

        mono_tsv_row.append([final_out_path + new_mono_name, text, round(clip_len,2)])
        cut_audio(output_dir + "mono/", new_mono_name, mono_audio, round(float(segment_start),2) , round(float(time),2))


get_parameters()

file = open(dataset_file, "r")
loaded_input_file = json.loads(file.read())
file.close()

index = 0
path = loaded_input_file["path"]
for directory in loaded_input_file["data"]:
    if "aligned-data" in directory and "prep-data-alignment" in directory:
        stereo_out_path = path + directory["dir-name"] + "/training-data/stereo/"
        if stereo:
            Path(stereo_out_path).mkdir(parents=True, exist_ok=True)

        mono_out_path = path + directory["dir-name"] + "/training-data/mono/"
        Path(mono_out_path).mkdir(parents=True, exist_ok=True)

        for ctm_file in directory["aligned-data"]:
            ctm_file_path = path + directory["dir-name"] + "/aligned-data/" + ctm_file["ctm-file"]
            file_ctm = open(ctm_file_path, "r")

            audio_name = ctm_file["ctm-file"].split(".")[0] + ".wav"

            mono_audio_path = path + directory["dir-name"] + "/prep-data-alignment/mono/" + audio_name
            mono_audio = pydub.AudioSegment.from_file(mono_audio_path)

            stereo_audio = None
            if stereo:
                stereo_audio_path = path + directory["dir-name"] + "/prep-data-alignment/stereo/" + audio_name
                stereo_audio = pydub.AudioSegment.from_file(stereo_audio_path)

            output_dir_path = path + directory["dir-name"] + "/training-data/"
            compute_cuts(file_ctm, 30, mono_audio, stereo_audio, output_dir_path, ctm_file["ctm-file"])

file.close()
write_to_tsv()