#!/usr/bin/env python3
import os
import sys
import argparse
import tempfile

import pandas as pd

import assemblyai
import utils
from set_project_markers import clear_markers, insert_chapters


VALID_STEPS = [1, 2, 3]

TRANSCRIPT_CONFIG = {
        "custom_spelling": [
            {"from": ["Christina"], "to": "Krystyna"},
            {"from": ["Krin", "Corrinne", "krin", "crin", "corinne", "Karen"], "to": "Corinne"},
            {"from": ["Antislock"], "to": "Anti-Slut"},
            {"from": ["anti fletching"], "to": "Anti-Slut-Shaming"},
            {"from": ["sorry about last night's show@gmail.com"], "to": "sorryaboutlastnightshow@gmail.com"}
            ],
        "word_boost": ["anti-slut", "anti-slut-shaming", "Guys We Fucked", "Corinne", "Krystyna", "sorryaboutlastnightshow@gmail.com"],
        "language_code": "en_us",
        "auto_highlights": True,
        "auto_chapters": True,
        "entity_detection": True,
        "iab_categories": True,
        "speaker_labels": True
    }


def main(argv):
    args = parse_args(argv)
    steps = args.steps
    steps.sort()
    id_override = args.id
    xlsx_override = args.xlsx

    # Validate steps
    for step in steps:
        if step not in VALID_STEPS:
            print(f"step {step} is not a valid step")
            return -1

    pymiere_proj, all_markers = utils.setup_pymiere()
    temp_audio = None
    xlsx_file = xlsx_override
    transcript_id = id_override

    for step in steps:
        if step == 1:
            print("== Extracting audio from project")
            temp_audio, extract_result = utils.extract_project_audio(pymiere_proj)
            print(f"  -- {extract_result}")
            print(f"  -- Audio: {temp_audio}")
            print("== DONE")
        elif step == 2:
            print("== Getting transcript")
            if temp_audio is None and id_override is None:
                print(f"temp_audio is missing. Please include step 1")
                return -1
            if transcript_id:
                print(f"  -- Using ID override: {transcript_id}")
            else:
                print("  -- Uploading file")
                upload_response = assemblyai.upload_file(temp_audio)
                audio_url = upload_response["upload_url"]
                transcript_response = assemblyai.get_transcript(audio_url, TRANSCRIPT_CONFIG)
                transcript_id = transcript_response["id"]
                print(f"  -- Transcript ID: {transcript_id}")
            print("  -- Waiting for data")
            transcript_json = assemblyai.poll_for_transcript(transcript_id, log=False)
            print("  -- Data ready")
            print("  -- Saving transcript.xlsx")
            xlsx_file = os.path.join(tempfile.mkdtemp(), "transcript.xlsx")
            assemblyai.write_transcript_to_excel(transcript_json, xlsx_file)
            print("== DONE")
        elif step == 3:
            print("== Updating Markers")
            if xlsx_file is None:
                print(f"xlsx_file is missing. Please include step 2 or use override")
                return -1
            clear_markers(all_markers)
            transcript_data = pd.read_excel(xlsx_file, sheet_name='chapters', index_col=None,
                                            header=0).transpose().to_dict().values()
            insert_chapters(all_markers, transcript_data)
            print("== DONE")
    return 0


def parse_args(argv):
    parser = argparse.ArgumentParser('Export audio from active premiere sequence')
    parser.add_argument('-s', '--steps', type=int, nargs='+', help='Steps execute can be one or more\n'
                                                                   '1: extract audio\n'
                                                                   '2: upload/get transcript\n'
                                                                   '3: insert markers\n'
                                                                   'example: 1 2')
    parser.add_argument('--id', help='Force transcript id for step 2')
    parser.add_argument('--xlsx', help='Force xlsx file for step 3')
    return parser.parse_args(args=argv)


if __name__ == '__main__':
    exit(main(sys.argv[1:]))
