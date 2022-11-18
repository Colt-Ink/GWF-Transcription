# run.py

import os
import argparse
import time
from main import run_transcription

# Get time of script run:
start_time = time.time()

# create the parser
parser = argparse.ArgumentParser(description="Transcribe a file with AssemblyAI")

# add the arguments ("-f" for the file path, "-t" for optional output title)
parser.add_argument("-f", "--file", help="File path to transcribe")
parser.add_argument("-t", "--title", help="Title of output file")

# parse the arguments
args = parser.parse_args()

# get the file path from the arguments
file_path = args.file

# get the title from the arguments
title = args.title

# if the title is not provided, set it to the file name
if title is None:
    title = file_path.split("/")[-1]

# run the transcription
run_transcription(file_path, title)

# print the time it took to run the script
print(f"Transcription took {time.time() - start_time} seconds")