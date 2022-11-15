import os
import argparse
from main import run_transcription

# create the parser
parser = argparse.ArgumentParser(description="Transcribe a file with AssemblyAI")

# add the arguments ("-f" for the file path, "-t" for optional output title)
parser.add_argument("-f", "--file_path", help="Path to the file to be transcribed", required=True)
parser.add_argument("-t", "--title", help="Title of the output file", required=False)

# parse the arguments
args = parser.parse_args()

# get the file path
file_path = args.file_path

# get the title
title = args.title

# if the title is not provided, use the file name
if not title:
    title = os.path.splitext(os.path.basename(file_path))[0]

# create the output file path
output_file_path = f"{title}.xlsx"

# run the transcription
run_transcription(file_path, output_file_path)