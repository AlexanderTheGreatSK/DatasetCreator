"""
    clip-cutter.py

    Author: xokruc00
    Email: xokruc00@fit.vutbr.cz

    This script will sanitize text ane cut audio file to the text segment included in the transcription text file.
    It will create a new directory for each audio with a stereo and mono version of the audio.

    Input:
        -d / --dataset - path to dataset.json

"""

import sys
import getopt
import json
import re
from pathlib import Path

import pydub

input_file = None

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

    print(input_file)

def calculate_seconds(start_time, end_time):
    return end_time - start_time

def cut_audio(path, audio, start_raw, end_raw):
    start = 0
    end = 0

    start_split = start_raw.split(":")
    if len(start_split) == 3:
        start = int(start_split[0]) * 3600 + int(start_split[1]) * 60 + int(start_split[2])
    elif len(start_split) == 2:
        start = int(start_split[0]) * 60 + int(start_split[1])
    else:
        start = start_raw

    end_split = end_raw.split(":")
    if len(end_split) == 3:
        end = int(end_split[0]) * 3600 + int(end_split[1]) * 60 + int(end_split[2])
    elif len(end_split) == 2:
        end = int(end_split[0]) * 60 + int(end_split[1])
    else:
        end = start_raw

    segment = audio[start*1000:end*1000]
    segment.export(path + ".wav", format="wav")
    return calculate_seconds(start, end)

def line_sanitizer(line):
    line = re.sub(r"[\(\[\{].*?[\)\]\}]", "", line)
    line = re.sub(r"#", "", line)
    line = re.sub(r"\.{2,}", " ", line)
    line = re.sub(r"/{2,}", "", line)
    line = re.sub(r"\s+", " ", line)


    return line


def process_text(txt_file, stereo_output, mono_output, name, stereo_audio_path, mono_audio_path, path):
    time_segment_found = False
    text_segment = ""
    time_segment = ""

    stereo_audio = pydub.AudioSegment.from_file(path + stereo_audio_path)
    mono_audio = pydub.AudioSegment.from_file(path + mono_audio_path)

    seconds_time = 0

    for line in txt_file:
        if re.search(r"\b\d{2}:\d{2}\s*[–—-]\s*\d{2}:\d{2}\b",line) is None and time_segment_found:
            if ":" in line:
                line_split = line.split(":", 1)
                line_sanitized = line_sanitizer(line_split[1])
                text_segment = text_segment + line_sanitized.strip() + " "
            else:
                line_sanitized = line_sanitizer(line)
                text_segment = text_segment + line_sanitized.strip() + " "
        elif re.search(r"\b\d{2}:\d{2}:\d{2}\s*[–—-]\s*\d{2}:\d{2}:\d{2}\b",line) is not None:
            line = re.sub(r"(\b\d{2}:\d{2}:\d{2})\s*[–—-]\s*(\d{2}:\d{2}:\d{2}\b)", r"\1-\2", line)
            if text_segment != "":
                Path(stereo_output).mkdir(parents=True, exist_ok=True)
                Path(mono_output).mkdir(parents=True, exist_ok=True)

                split_time = time_segment.split("-")
                text_time_segment = split_time[0] + "-" + split_time[1]

                stereo_output_text_file = open(stereo_output + name + "_xs_" + text_time_segment + ".txt", "w")
                mono_output_text_file = open(mono_output + name + "_xs_" + text_time_segment + ".txt", "w")

                stereo_output_text_file.write(text_segment)
                mono_output_text_file.write(text_segment)

                stereo_output_text_file.close()
                mono_output_text_file.close()

                seconds_time += cut_audio(stereo_output + name + "_xs_" + text_time_segment, stereo_audio, split_time[0], split_time[1])
                cut_audio(mono_output + name + "_xs_" + text_time_segment, mono_audio, split_time[0], split_time[1])

                text_segment = ""
                time_segment = re.search(r"\b\d{2}:\d{2}:\d{2}\s*[–—-]\s*\d{2}:\d{2}:\d{2}\b",line).group()
            else:
                time_segment = re.search(r"\b\d{2}:\d{2}:\d{2}\s*[–—-]\s*\d{2}:\d{2}:\d{2}\b",line).group()

            if not time_segment_found:
                time_segment_found = True
        elif re.search(r"\b\d{2}:\d{2}:\d{2}\s*[–—-]\s*\d{2}:\d{2}:\d{2}\b",line) is None and re.search(r"\b\d{2}:\d{2}\s*[–—-]\s*\d{2}:\d{2}\b",line) is not None:
            line = re.sub(r"(\b\d{2}:\d{2})\s*[–—-]\s*(\d{2}:\d{2}\b)", r"\1-\2", line)
            if text_segment != "":
                Path(stereo_output).mkdir(parents=True, exist_ok=True)
                Path(mono_output).mkdir(parents=True, exist_ok=True)

                split_time = time_segment.split("-")
                text_time_segment = split_time[0] + "-" + split_time[1]

                stereo_output_text_file = open(stereo_output + name + "_xs_" + text_time_segment + ".txt", "w")
                mono_output_text_file = open(mono_output + name + "_xs_" + text_time_segment + ".txt", "w")

                stereo_output_text_file.write(text_segment)
                mono_output_text_file.write(text_segment)

                stereo_output_text_file.close()
                mono_output_text_file.close()


                seconds_time += cut_audio(stereo_output + name + "_xs_" + text_time_segment, stereo_audio, split_time[0], split_time[1])
                cut_audio(mono_output + name + "_xs_" + text_time_segment, mono_audio, split_time[0], split_time[1])

                text_segment = ""
                time_segment = re.search(r"\b\d{2}:\d{2}\s*[–—-]\s*\d{2}:\d{2}\b",line).group()
            else:
                time_segment = re.search(r"\b\d{2}:\d{2}\s*[–—-]\s*\d{2}:\d{2}\b",line).group()

            if not time_segment_found:
                time_segment_found = True
        else:
            print(line)


    if text_segment != "":
        Path(stereo_output).mkdir(parents=True, exist_ok=True)
        Path(mono_output).mkdir(parents=True, exist_ok=True)

        split_time = time_segment.split("-")
        text_time_segment = split_time[0] + "-" + split_time[1]

        stereo_output_text_file = open(stereo_output + name + "_xs_" + text_time_segment + ".txt", "w")
        mono_output_text_file = open(mono_output + name + "_xs_" + text_time_segment + ".txt", "w")

        stereo_output_text_file.write(text_segment)
        mono_output_text_file.write(text_segment)

        stereo_output_text_file.close()
        mono_output_text_file.close()

        split_time = time_segment.split("-")

        seconds_time += cut_audio(stereo_output + name + "_xs_" + text_time_segment, stereo_audio, split_time[0], split_time[1])
        cut_audio(mono_output + name + "_xs_" + text_time_segment, mono_audio, split_time[0], split_time[1])
    return seconds_time

get_parameters()

file = open(input_file, 'r')
loaded_input_file = json.loads(file.read())

path = loaded_input_file["path"]
aligned_time_sec = 0

for data in loaded_input_file["data"]:
    if "raw-text" in data and "stereo-original-audio" in data and "mono-original-audio" in data:
        txt_file = open(path + data["dir-name"] + "/" + data["raw-text"],"r")
        output_dir_stereo = path + data["dir-name"] + "/" + "prep-data-alignment/stereo/"
        output_dir_mono = path + data["dir-name"] + "/" + "prep-data-alignment/mono/"
        split = data["raw-text"].split(".")
        aligned_time_sec += process_text(txt_file, output_dir_stereo, output_dir_mono, split[0], data["stereo-original-audio"], data["mono-original-audio"], path + data["dir-name"] + "/")

file.close()
loaded_input_file["total-aligned-seconds"] = aligned_time_sec
json_file = open(input_file, "w")
json_file.write(json.dumps(loaded_input_file))
json_file.close()
