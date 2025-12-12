import sys
import getopt
import json
import re
from pathlib import Path

input_file = None
output_file = None

def get_parameters():
    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, "hp:o:", ["file_path=","output_file="])
    except:
        print("Error")
        exit(1)

    for opt, arg in opts:
        if opt in ("-p", "--path"):
            global input_file
            input_file = arg
        if opt in ("-o", "--out"):
            global output_file
            output_file = arg

    print(input_file)
    print(output_file)

def line_sanitizer(line):

    if re.search(r"\b\d{1,2}:\d{2}:\d{2}\s*[–—-]\s*\d{1,2}:\d{2}:\d{2}\b",line) is not None:
        print("1 found line: ", line)
        return ""
    elif re.search(r"\b\d{1,2}:\d{2}:\d{2}\s*[–—-]\s*\d{1,2}:\d{2}:\d{2}\b",line) is None and re.search(r"\b\d{2}:\d{2}\s*[–—-]\s*\d{2}:\d{2}\b",line) is not None:
        print("2 found line: ", line)
        return ""
    else:
        if ":" in line:
            line = line.split(":")[1]

        line = line.replace("…", "")
        line = re.sub(r"[\(\[\{].*?[\)\]\}]", "", line)
        line = re.sub(r"#", "", line)
        line = re.sub(r"\.{2,}", " ", line)
        line = re.sub(r"/{2,}", "", line)
        line = re.sub(r"\s+", " ", line)
        line = line.strip()
    return line

get_parameters()

file = Path(input_file)
if not file.exists():
    raise FileNotFoundError(f"File not found: {file}")
outfile = Path(output_file)
if not outfile.exists():
    raise FileNotFoundError(f"File not found: {output_file}")

new_line = ""

with open(file, "r") as f:
    for line in f:
        new_line = line_sanitizer(line)
        if new_line != "":
            new_line += " "
            with open(outfile, "a") as of:
                of.write(new_line)