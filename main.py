#!/usr/bin/env python3
import argparse
import logging
import os
import re
import time
from collections import Counter

import xlsxwriter

import assemblyai


def transcript_time_to_timecode(transcript_time):
    hours, milliseconds = divmod(transcript_time, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    seconds = float(milliseconds) / 1000
    return '{:02}:{:02}:{:06.3f}'.format(int(hours), int(minutes), seconds)


def write_transcript_to_excel(transcript_json, excel_file_path):
    """
    Writes a transcript to an Excel file
    """
    workbook = xlsxwriter.Workbook(excel_file_path)
    worksheet_words = workbook.add_worksheet("words")

    # Write words
    worksheet_words.write(0, 0, "start")
    worksheet_words.write(0, 1, "end")
    worksheet_words.write(0, 2, "confidence")
    worksheet_words.write(0, 3, "speaker")
    worksheet_words.write(0, 4, "text")
    row = 1
    for word in transcript_json["words"]:
        worksheet_words.write(row, 0, transcript_time_to_timecode(word["start"]))
        worksheet_words.write(row, 1, transcript_time_to_timecode(word["end"]))
        worksheet_words.write(row, 2, word["confidence"])
        worksheet_words.write(row, 3, word["speaker"])
        worksheet_words.write(row, 4, word["text"])
        row += 1

    if transcript_json.get("paragraphs"):
        worksheet_paragraphs = workbook.add_worksheet("paragraphs")
        worksheet_paragraphs.write(0, 0, "start")
        worksheet_paragraphs.write(0, 1, "end")
        worksheet_paragraphs.write(0, 2, "text")
        row = 1
        for paragraph in transcript_json["paragraphs"]:
            worksheet_paragraphs.write(row, 0, transcript_time_to_timecode(paragraph["start"]))
            worksheet_paragraphs.write(row, 1, transcript_time_to_timecode(paragraph["end"]))
            worksheet_paragraphs.write(row, 2, paragraph["text"])
            row += 1
    else:
        logging.warning("no paragraphs were detected")

    # Write highlights
    if transcript_json["auto_highlights"]:
        if transcript_json["auto_highlights_result"]["status"] == "success":
            worksheet_highlights = workbook.add_worksheet("highlights")
            worksheet_highlights.write(0, 0, "start")
            worksheet_highlights.write(0, 1, "text")
            worksheet_highlights.write(0, 2, "count")
            worksheet_highlights.write(0, 3, "rank")
            row = 1
            for highlight in transcript_json["auto_highlights_result"]["results"]:
                timestamps = ','.join([transcript_time_to_timecode(inst["start"]) for inst in highlight["timestamps"]])
                worksheet_highlights.write(row, 0, timestamps)
                worksheet_highlights.write(row, 1, highlight["text"])
                worksheet_highlights.write(row, 2, highlight["count"])
                worksheet_highlights.write(row, 3, highlight["rank"])
                row += 1
        else:
            logging.warning("auto_highlights was not successful")
    else:
        logging.warning("auto_highlights were not configured")

    # Write chapters
    if transcript_json["auto_chapters"]:
        worksheet_chapters = workbook.add_worksheet("chapters")
        worksheet_chapters.write(0, 0, "start")
        worksheet_chapters.write(0, 1, "end")
        worksheet_chapters.write(0, 2, "summary")
        worksheet_chapters.write(0, 3, "gist")
        worksheet_chapters.write(0, 4, "headline")
        row = 1
        for chapter in transcript_json["chapters"]:
            worksheet_chapters.write(row, 0, transcript_time_to_timecode(chapter["start"]))
            worksheet_chapters.write(row, 1, transcript_time_to_timecode(chapter["end"]))
            worksheet_chapters.write(row, 2, chapter["summary"])
            worksheet_chapters.write(row, 3, chapter["gist"])
            worksheet_chapters.write(row, 4, chapter["headline"])
            row += 1
    else:
        logging.warning("chapters were not detected")

    # Write entities
    if transcript_json["entity_detection"]:
        worksheet_entities = workbook.add_worksheet("entities")
        worksheet_entities.write(0, 0, "start")
        worksheet_entities.write(0, 1, "end")
        worksheet_entities.write(0, 2, "text")
        worksheet_entities.write(0, 3, "entity_type")
        row = 1
        for entity in transcript_json["entities"]:
            worksheet_entities.write(row, 0, transcript_time_to_timecode(entity["start"]))
            worksheet_entities.write(row, 1, transcript_time_to_timecode(entity["end"]))
            worksheet_entities.write(row, 2, entity["text"])
            worksheet_entities.write(row, 3, entity["entity_type"])
            row += 1
    else:
        logging.warning("no entities were detected")

    # Write IAB categories
    if transcript_json["iab_categories"]:
        if transcript_json["iab_categories_result"]["status"] == "success":
            worksheet_iab_categories = workbook.add_worksheet("iab_categories")
            worksheet_iab_categories.write(0, 0, "labels")
            worksheet_iab_categories.write(0, 1, "count")
            row = 1
            label_list = []
            for iab_category in transcript_json["iab_categories_result"]["results"]:
                labels = ','.join([lab["label"] for lab in iab_category["labels"]])
                # new row for each ">"
                labels = labels.replace(">", ">\n")
                # add space after each comma
                labels = labels.replace(",", ", ")
                # add space before each capital letter
                labels = re.sub(r"([a-z])([A-Z])", r"\1 \2", labels)
                label_list.append(labels)

            counts = Counter()
            counts.update(label_list)

            for label, count in counts.items():
                worksheet_iab_categories.write(row, 0, label)
                worksheet_iab_categories.write(row, 1, count)
                row += 1
        else:
            logging.warning("iab_categories did not succeed")
    else:
        logging.warning("iab_categories were not configured")

    workbook.close()


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
            {"from": ["Krin", "Corrinne", "krin", "corinne"], "to": "Corinne"},
            {"from": ["Antislock"], "to": "Anti-Slut"},
            {"from": ["guys we fucked", "guys, we fucked"], "to": "Guys We Fucked"},
            ],
        "word_boost": ["Guys We Fucked", "Corinne", "Krystyna", "sorryaboutlastnightshow@gmail.com"],
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
    write_transcript_to_excel(transcript_json, f"{output_dir}/{title}.xlsx")

    print(f"Collecting {title}.srt")
    srtData = assemblyai.get_srt(transcript_id)
    with open(f"{output_dir}/{title}.srt", "w") as f:
        f.write(srtData)

    print(f"Transcription took {time.time() - start_time} seconds")
