# main.py:

import argparse
import sys
from api_communication import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Transcribe audio files using AssemblyAI API')
    parser.add_argument('--url', type=str, help='URL of audio file')
    parser.add_argument('--title', type=str, help='Title of transcript')
    args = parser.parse_args()

    if not args.url:
        print("Please provide a URL")
        sys.exit(1)
        
    if not args.title:
        print("Please provide a title")
        sys.exit(1)

    save_transcript(args.url, args.title)