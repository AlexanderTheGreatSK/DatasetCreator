"""
    This script pairs .txt, .doc(x) and its .waw, .mp3 and moves them to created new directory for them.

    @author: Alexander Okrucký <xokruc00@stud.fit.vutbr.cz>
"""
import json
import sys
import os as os
import getopt


def get_parameters():
    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, "hp:", ["path="])
    except:
        print("Error")
        exit(1)

    for opt, arg in opts:
        if opt in ("-p", "--path"):
            global input_path
            input_path = arg


def process_tree_json(file):
    tree = json.loads(file.read())
    files = tree[0]["contents"]

    stats = dict()
    target_path = tree[0]["name"]


    #for file in files:
        #if file["path"]

get_parameters()
command = "tree -J " + input_path + " > ./tmp.json"
os.popen(command).read()

tree_file = open("./tmp.json", "r")
process_tree_json(tree_file)

tree_file.close()
