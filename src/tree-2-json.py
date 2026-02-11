""""
    tree-2-json.py

    Author: xokruc00
    Email: xokruc00@fit.vutbr.cz

    This script creates dataset.json from directory structure. It uses unix command tree -J, to get a directory
    structure in json. This json is processed. During processing original audio will be converted to wav file.
    From converted wav file will be created its mono or stereo version.

    Input limitations:
        - in each directory should be only one wav file and one txt file
        - as a text, only txt is supported - doc, docx or other formats will be ignored
        - if you have multiple text files for one audio - put it in different directory with copy of the audio file
        - audio types supported: .wav, .mp3, .flac, .m4a

    Parameters:
        -i --input path-to-data
        -y --yes - confirmation
        -t --no-transformation - audio is not transformed ,it stays as it is

    Output:
        It will create dataset.json in current directory
"""
import getopt
import os as os
import sys
import json
from pydub import AudioSegment
from pydub.utils import mediainfo

confirmation = False
transform = True

def get_parameters():
    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, "hyti:", ["input=","yes","no-transformation"])
    except:
        print("Error")
        exit(1)

    for opt, arg in opts:
        if opt in ("-i", "--input"):
            global input_file
            input_file = arg
        elif opt in ("-y", "--yes"):
            global confirmation
            confirmation = True
        elif opt in ("-t", "--no-transformation"):
            global transform
            transform = False



# This function detects multiple dots in filename
def more_dots_in_name(filename):
    split = filename.split(".")
    if len(split) == 2:
        return False
    else:
        return True

# checks if file is audio file
def is_file_audio(filename):
    split = filename.split(".")
    file_extension = split[1].lower()
    if file_extension == "mp3" or file_extension == "wav" or file_extension == "flac" or file_extension == "m4a":
        return True
    else:
        return False


def get_audio_type(filename):
    if not is_file_audio(filename):
        return None
    return filename.split(".")[1].lower()

def audio_to_wav(path, filename):
    filetype = get_audio_type(filename)

    if filetype != "wav":
        sound = AudioSegment.from_file(path + filename)
        split = filename.split(".")
        wav_name = split[0] + ".wav"
        sound.export(path + wav_name, format="wav")
        return wav_name

def create_audio_info_json(sample_rate, duration, channels, codec_name):
    media_info_json = {}
    media_info_json["sample-rate"] = int(sample_rate)
    media_info_json["duration-sec"] = round(float(duration),2)
    media_info_json["channels"] = int(channels)
    media_info_json["codec-name"] = codec_name
    return media_info_json, float(duration)

# replaces all dots in file name for _
def fix_more_dots_in_name(path, filename):
    split = filename.split(".")
    fixed_name = ""

    for i in range(len(split) - 1):
        fixed_name = fixed_name + split[i] + "_"
    fixed_name = fixed_name + "." + split[-1]
    return fixed_name

def rename_text_file(path, old_name, new_name):
    os.rename(path + old_name, path + new_name)

def get_filename(filename):
    return filename.split(".")[0]

def text_audio_name_compare(path, audio_name, text_name):
    if audio_name == text_name:
        return text_name
    else:
        rename_text_file(path, text_name, audio_name)
        return audio_name

# calculates aligned time from filename
def calculate_aligned_time(filename):
    raw_name = filename.split(".")[0]
    time_interval = raw_name.split("_xs_")[1]

    split = time_interval.split("-")
    start_split = split[0].split(":")
    end_split = split[1].split(":")

    seconds_start = 0
    seconds_end = 0

    if len(start_split) == 3:
        seconds_start = 3600 * int(start_split[0])
        seconds_end = 3600 * int(end_split[0])

        seconds_start += 60 * int(start_split[1])
        seconds_end += 60 * int(end_split[1])

        seconds_end += int(end_split[2])
        seconds_start += int(start_split[2])
    else:
        seconds_start += 60 * int(start_split[0])
        seconds_end += 60 * int(end_split[0])

        seconds_end += int(end_split[1])
        seconds_start += int(start_split[1])

    return seconds_end - seconds_start

def create_mono_audio(path, filename):
    if "stereo" not in filename and "mono" not in filename:
        new_name = filename.split(".")[0] + "-mono.wav"

        sound = AudioSegment.from_wav(path + filename)
        sound = sound.set_channels(1)
        sound.export(path + new_name, format="wav")
        return new_name
    else:
        return filename

def create_stereo_audio(path, filename):
    if "stereo" not in filename and "mono" not in filename:
        new_name = filename.split(".")[0] + "-stereo.wav"

        sound = AudioSegment.from_wav(path + filename)
        sound = sound.set_channels(2)
        sound.export(path + new_name, format="wav")
        return new_name
    else:
        return filename

def process_tree_json(file):
    total_duration = 0
    total_audio_files = 0
    total_directories = 0
    total_text_files = 0
    total_aligned_seconds = 0

    input_json = json.loads(file.read())
    json_out = {}

    max_dir = len(input_json[0]["contents"])
    current_processed = 0

    if not input_json[0]["name"].endswith("/"):
        json_out["path"] = input_json[0]["name"] + "/"
    else:
        json_out["path"] = input_json[0]["name"]
    json_out["data"] = []
    path = json_out["path"]

    for item in input_json[0]["contents"]:
        current_processed += 1
        if item["type"] == "directory":
            total_directories += 1
            clip = {}
            clip["dir-name"] = item["name"]

            clip["original-audio"] = ""

            text_file_name = ""
            audio_file_name = ""

            if item["contents"] is not None:
                for subitem in item["contents"]:
                    fixed_name = ""
                    if subitem["type"] == "file":
                        if more_dots_in_name(subitem["name"]):
                            fixed_name = fix_more_dots_in_name(path, subitem["name"])
                            os.rename(path + item["name"] + "/" + subitem["name"], path + item["name"] + "/" + fixed_name)
                            subitem["name"] = fixed_name

                        if subitem["name"].endswith(".txt"):
                            if audio_file_name != "":
                                text_file_name = get_filename(subitem["name"])
                                subitem["name"] = text_audio_name_compare(path, audio_file_name, text_file_name)

                            clip["raw-text"] = subitem["name"]
                            total_text_files += 1
                        elif is_file_audio(subitem["name"]):
                            if subitem["name"].endswith(".wav") and clip["original-audio"] == "":
                                total_audio_files += 1
                                clip["original-audio"] = subitem["name"]
                                media_info = mediainfo(path + item["name"] + "/" + subitem["name"])

                                clip["audio-info"], duration = create_audio_info_json(media_info["sample_rate"],media_info["duration"],media_info["channels"],media_info["codec_name"])
                                curr_path = path + item["name"] + "/"
                                if clip["audio-info"]["channels"] == 1:
                                    clip["mono-original-audio"] = subitem["name"]
                                    if transform:
                                        clip["stereo-original-audio"] = create_stereo_audio(curr_path, subitem["name"])
                                else:
                                    clip["stereo-original-audio"] = subitem["name"]
                                    if transform:
                                        clip["mono-original-audio"] = create_mono_audio(curr_path, subitem["name"])

                                total_duration += duration
                            elif clip["original-audio"] == "":
                                total_audio_files += 1
                                new_name = audio_to_wav(path + item["name"] + "/", subitem["name"])
                                clip["original-audio"] = new_name
                                media_info = mediainfo(path + item["name"] + "/" + new_name)
                                clip["audio-info"], duration = create_audio_info_json(media_info["sample_rate"],media_info["duration"],media_info["channels"],media_info["codec_name"])

                                curr_path = path + item["name"] + "/"
                                if transform:
                                    if clip["audio-info"]["channels"] == 1:
                                        clip["mono-original-audio"] = clip["original-audio"]
                                        clip["stereo-original-audio"] = create_stereo_audio(curr_path, clip["original-audio"])
                                    else:
                                        clip["mono-original-audio"] = create_mono_audio(curr_path, clip["original-audio"])
                                        clip["stereo-original-audio"] = clip["original-audio"]

                                total_duration += duration
                    elif subitem["type"] == "directory":
                        if "prep-data-alignment" in subitem["name"]:
                            text_files = 0
                            audio_files = 0
                            aligned_time = 0
                            stereo_prep_data_alignment = []
                            mono_prep_data_alignment = []

                            clip["prep-data-alignment"] = {}

                            if "contents" in subitem:
                                for audio_type in subitem["contents"]:
                                    if audio_type["name"] == "stereo" and audio_type["type"] == "directory":
                                        if "contents" not in subitem:
                                            clip["prep-data-alignment"] = {}
                                            clip["prep-data-alignment"]["stereo"] = stereo_prep_data_alignment
                                            continue

                                        for prep_data_file in audio_type["contents"]:
                                            if prep_data_file["type"] == "file":
                                                if prep_data_file["name"].endswith(".txt"):
                                                    text_files += 1
                                                    tmp_seconds = calculate_aligned_time(prep_data_file["name"])
                                                    aligned_time += tmp_seconds
                                                    total_aligned_seconds += tmp_seconds
                                                    tmp_data = {}
                                                    tmp_data["duration-sec"] = tmp_seconds
                                                    tmp_data["text"] = prep_data_file["name"]
                                                    stereo_prep_data_alignment.append(tmp_data)
                                                if prep_data_file["name"].endswith(".wav"):
                                                    audio_files += 1
                                                    name = prep_data_file["name"].split(".")[0]
                                                    for alignment in stereo_prep_data_alignment:
                                                        if alignment["text"].split(".")[0] == name:
                                                            alignment["audio"] = prep_data_file["name"]
                                                            break
                                        clip["prep-data-alignment"]["stereo"] = stereo_prep_data_alignment

                                    elif audio_type["name"] == "mono" and audio_type["type"] == "directory":
                                        if "contents" not in subitem:
                                            clip["prep-data-alignment"] = {}
                                            clip["prep-data-alignment"]["mono"] = mono_prep_data_alignment
                                            continue

                                        for prep_data_file in audio_type["contents"]:
                                            if prep_data_file["type"] == "file":
                                                if prep_data_file["name"].endswith(".txt"):
                                                    text_files += 1
                                                    tmp_seconds = calculate_aligned_time(prep_data_file["name"])
                                                    aligned_time += tmp_seconds
                                                    total_aligned_seconds += tmp_seconds
                                                    tmp_data = {}
                                                    tmp_data["duration-sec"] = tmp_seconds
                                                    tmp_data["text"] = prep_data_file["name"]
                                                    mono_prep_data_alignment.append(tmp_data)
                                                if prep_data_file["name"].endswith(".wav"):
                                                    audio_files += 1
                                                    name = prep_data_file["name"].split(".")[0]
                                                    for alignment in mono_prep_data_alignment:
                                                        if alignment["text"].split(".")[0] == name:
                                                            alignment["audio"] = prep_data_file["name"]
                                                            break
                                        clip["prep-data-alignment"]["mono"] = mono_prep_data_alignment
                        elif "aligned-data" in subitem["name"]:
                            print("Aligned data")
                        elif "training-data" in subitem["name"]:
                            print("Fine-tuned data")
            json_out["data"].append(clip)

    json_out["total-duration-sec"] = round(total_duration,2)
    json_out["total-audio-files"] = total_audio_files
    json_out["total-directories"] = total_directories
    json_out["total-text-files"] = total_text_files
    json_out["total-aligned-seconds"] = total_aligned_seconds

    raw_data = json.dumps(json_out)
    json_file = open("./dataset.json", "w")
    json_file.write(raw_data)
    json_file.close()

get_parameters()

if input_file is None:
    print("No input file")
    exit(1)

command = "tree -J " + input_file + " > ./tmp.json"
os.popen(command).read()

tree_file = open("./tmp.json", "r")

if not confirmation:

    for line in tree_file:
        print(line, end="")
    tree_file.close()
    print("\n Is this correct?")
    confirm = input("Press y to continue...\n")
    if confirm != "y" and confirm != "Y" and confirm != "yes" and confirm != "YES":
        print("\nExiting")
        tree_file.close()
        exit(0)

tree_file = open("./tmp.json", "r")
process_tree_json(tree_file)


tree_file.close()
