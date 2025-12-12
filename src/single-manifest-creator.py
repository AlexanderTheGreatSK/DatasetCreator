import sys
import getopt
import json
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