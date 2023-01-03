#!/usr/bin/env python3
import argparse
import os
import time

import assemblyai


def parse_args():
    parser = argparse.ArgumentParser(description="Transcribe a file with AssemblyAI")
    parser.add_argument("-f", "--file", help="File path to transcribe")
    parser.add_argument("-t", "--title", help="Optional: Title of output file. Defaults to name of input file basename")
    parser.add_argument("-i", "--id", help='existing transcript id')
    parser.add_argument("-o", "--output-dir",
                        help='Optional: Directory to write output file to. Defaults to same directory as input file.')
    return parser.parse_args()


if __name__ == '__main__':
    # Get time of script run:
    start_time = time.time()

    args = parse_args()
    file_path = args.file
    title = args.title
    id_override = args.id
    output_dir = args.output_dir
    if title is None:
        title = os.path.splitext(os.path.basename(file_path))[0]
    if output_dir is None:
        output_dir = os.path.dirname(file_path)
    else:
        output_dir = os.path.abspath(output_dir)

    # TODO: arguments can modify base_data to include more detections.
    base_data = {
        "custom_spelling": [ 
            {"from": ["Christina"], "to": "Krystyna"},
            {"from": ["Krin", "Corrinne", "krin", "crin", "corinne, Karen"], "to": "Corinne"},
            {"from": ["Antislock"], "to": "Anti-Slut"},
            {"from": ["anti fletching"], "to": "Anti-Slut-Shaming"},
            {"from": ["sorry about last night's show@gmail.com"], "to": "sorryaboutlastnightshow@gmail.com"}
            ],
        "word_boost": ["anti-slut", "anti-slut-shaming", "Guys We Fucked", "Corinne", "Krystyna", "sorryaboutlastnightshow@gmail.com"],
        "auto_highlights": True,
        "auto_chapters": True,
        "entity_detection": True,
        "iab_categories": True,
        "speaker_labels": True
    }

    if not id_override:
        # Upload the file
        upload_response_json = assemblyai.upload_file(file_path)
        audio_url = upload_response_json["upload_url"]
        print(f"Uploaded {file_path}")

        # Get the transcript
        transcript_response_json = assemblyai.get_transcript(audio_url, base_data)
        transcript_id = transcript_response_json["id"]
        print(f"Transcript ID: {transcript_id}")
    else:
        transcript_id = id_override

    print("Polling...")
    transcript_json = assemblyai.poll_for_transcript(transcript_id)

    print("Getting paragraphs...")
    transcript_json["paragraphs"] = assemblyai.get_paragraphs(transcript_id)

    print(f"Writing {title}.xlsx")
    assemblyai.write_transcript_to_excel(transcript_json, f"{output_dir}/{title}.xlsx")

    print(f"Writing {title}.json")
    assemblyai.write_transcript_to_json(transcript_json, f"{output_dir}/{title}.json")

    print(f"Collecting {title}.srt")
    srtData = assemblyai.get_srt(transcript_id)
    with open(f"{output_dir}/{title}.srt", "w") as f:
        f.write(srtData)

    print(f"Transcription took {time.time() - start_time} seconds")
