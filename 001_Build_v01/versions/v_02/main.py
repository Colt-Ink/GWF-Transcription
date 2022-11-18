import argparse

from api_communication import save_transcript

parser = argparse.ArgumentParser()
parser.add_argument("--url", help="Audio URL")
parser.add_argument("--title", help="Title of audio")
args = parser.parse_args()

save_transcript(args.url, args.title)