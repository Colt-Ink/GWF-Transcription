# main.py:

import requests
import json
import os
import pandas as pd
import time
import xlsxwriter
import base64
import pprint
from tqdm import tqdm
from api_secrets import API_KEY_ASSEMBLYAI

# upload
upload_endpoint = "https://api.assemblyai.com/v2/upload"
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"

headers_auth_only = {'authorization': API_KEY_ASSEMBLYAI}

headers = {
    "authorization": API_KEY_ASSEMBLYAI,
    "content-type": "application/json"
}

CHUNK_SIZE = 5_242_880  # 5MB

# Create a function that uploads a local audio file to the Assembly AI transcript api with requests for transcript, shows a progress bar while it waits for the upload to finish, then polls for a status of "complete", and then gets all of the JSON data and write it to multiple sheets in an Excel spreadsheet.

def upload_file(file_path):
    """
    Uploads a file to AssemblyAI with a progress bar
    """
    def read_file(file_path):
        with open(file_path, "rb") as f:
            while True:
                data = f.read(CHUNK_SIZE)
                if not data:
                    break
                yield data
        
    upload_response = requests.post(
        upload_endpoint,
        headers=headers_auth_only,
        data=tqdm(read_file(file_path), total=os.path.getsize(file_path)//CHUNK_SIZE, unit="chunk")
    )
    upload_response.raise_for_status()
    return upload_response.json()["upload_url"]


def get_transcript(audio_url):
    """
    Gets a transcript from AssemblyAI
    """
    # create the data
    data = {
        "audio_url": audio_url,
        "model": "default",
        "speaker_channels": "combined",
        "speaker_labels": True,
        "confidence_threshold": 0.5,
        "auto_highlights": True,
        "iab_categories": True,
        "auto_chapters": True,
        "entity_detection": True
    }

    # get the transcript
    response = requests.post(transcript_endpoint, json=data, headers=headers)
    return response.json()["id"]

# poll for completion
def poll(transcript_id):
    """
    Polls for completion of a transcript
    """
    polling_endpoint = transcript_endpoint + '/' + transcript_id
    polling_response = requests.get(polling_endpoint, headers=headers)
    return polling_response.json()

def get_transcription_result(url):
    transcribe_id = get_transcript(url)
    while True:
        data = poll(transcribe_id)
        if data['status'] == 'completed':
            return data, None
        elif data['status'] == "error":
            return data, data['error']
        # Wait 30 seconds between polls and print "Checking again in 30 secs" with "Elapsed time:" {time elapsed since upload start}
        from run import start_time
        time.sleep(30)
        print("Checking again in 30 secs")
        print("Elapsed time:", time.time() - start_time)

def create_spreadsheet(data, output_file_path):
    """
    Creates an Excel spreadsheet with the data
    """
    # create the workbook
    workbook = xlsxwriter.Workbook(output_file_path)

    # create the worksheets
    worksheet_transcript = workbook.add_worksheet("Transcript")
    worksheet_speakers = workbook.add_worksheet("Speakers")
    worksheet_highlights = workbook.add_worksheet("Highlights")
    worksheet_chapters = workbook.add_worksheet("Chapters")
    worksheet_entities = workbook.add_worksheet("Entities")
    worksheet_iab_categories = workbook.add_worksheet("IAB Categories")

    # create the formats
    bold = workbook.add_format({"bold": True})

    # write the transcript data
    worksheet_transcript.write(0, 0, "Transcript ID", bold)
    worksheet_transcript.write(0, 1, data["id"])
    worksheet_transcript.write(1, 0, "Transcript Text", bold)
    worksheet_transcript.write(1, 1, data["text"])
    worksheet_transcript.write(2, 0, "Transcript URL", bold)
    worksheet_transcript.write(2, 1, data["transcript_url"])
    worksheet_transcript.write(3, 0, "Confidence Score", bold)
    worksheet_transcript.write(3, 1, data["confidence"])
    worksheet_transcript.write(4, 0, "Processing Time", bold)
    worksheet_transcript.write(4, 1, data["processing_seconds"])
    worksheet_transcript.write(5, 0, "Status", bold)
    worksheet_transcript.write(5, 1, data["status"])

    # write the speaker data
    worksheet_speakers.write(0, 0, "Speaker ID", bold)
    worksheet_speakers.write(0, 1, "Speaker Name", bold)
    worksheet_speakers.write(0, 2, "Speaker Channel", bold)
    worksheet_speakers.write(0, 3, "Speaker Start Time", bold)
    worksheet_speakers.write(0, 4, "Speaker End Time", bold)
    worksheet_speakers.write(0, 5, "Speaker Confidence", bold)
    worksheet_speakers.write(0, 6, "Speaker Text", bold)
    for i, speaker in enumerate(data["speakers"]):
        worksheet_speakers.write(i + 1, 0, speaker["id"])
        worksheet_speakers.write(i + 1, 1, speaker["name"])
        worksheet_speakers.write(i + 1, 2, speaker["channel"])
        worksheet_speakers.write(i + 1, 3, speaker["start_time"])
        worksheet_speakers.write(i + 1, 4, speaker["end_time"])
        worksheet_speakers.write(i + 1, 5, speaker["confidence"])
        worksheet_speakers.write(i + 1, 6, speaker["text"])

    # write the highlight data
    worksheet_highlights.write(0, 0, "Highlight ID", bold)
    worksheet_highlights.write(0, 1, "Highlight Start Time", bold)
    worksheet_highlights.write(0, 2, "Highlight End Time", bold)
    worksheet_highlights.write(0, 3, "Highlight Text", bold)
    for i, highlight in enumerate(data["highlights"]):
        worksheet_highlights.write(i + 1, 0, highlight["id"])
        worksheet_highlights.write(i + 1, 1, highlight["start_time"])
        worksheet_highlights.write(i + 1, 2, highlight["end_time"])
        worksheet_highlights.write(i + 1, 3, highlight["text"])

    # write the chapter data
    worksheet_chapters.write(0, 0, "Chapter ID", bold)
    worksheet_chapters.write(0, 1, "Chapter Start Time", bold)
    worksheet_chapters.write(0, 2, "Chapter End Time", bold)
    worksheet_chapters.write(0, 3, "Chapter Text", bold)
    for i, chapter in enumerate(data["chapters"]):
        worksheet_chapters.write(i + 1, 0, chapter["id"])
        worksheet_chapters.write(i + 1, 1, chapter["start_time"])
        worksheet_chapters.write(i + 1, 2, chapter["end_time"])
        worksheet_chapters.write(i + 1, 3, chapter["text"])

    # write the entity data
    worksheet_entities.write(0, 0, "Entity ID", bold)
    worksheet_entities.write(0, 1, "Entity Start Time", bold)
    worksheet_entities.write(0, 2, "Entity End Time", bold)
    worksheet_entities.write(0, 3, "Entity Text", bold)
    worksheet_entities.write(0, 4, "Entity Type", bold)
    worksheet_entities.write(0, 5, "Entity Subtype", bold)
    worksheet_entities.write(0, 6, "Entity Score", bold)
    for i, entity in enumerate(data["entities"]):
        worksheet_entities.write(i + 1, 0, entity["id"])
        worksheet_entities.write(i + 1, 1, entity["start_time"])
        worksheet_entities.write(i + 1, 2, entity["end_time"])
        worksheet_entities.write(i + 1, 3, entity["text"])
        worksheet_entities.write(i + 1, 4, entity["type"])
        worksheet_entities.write(i + 1, 5, entity["subtype"])
        worksheet_entities.write(i + 1, 6, entity["score"])

    # write the iab category data
    worksheet_iab_categories.write(0, 0, "IAB Category ID", bold)
    worksheet_iab_categories.write(0, 1, "IAB Category Name", bold)
    worksheet_iab_categories.write(0, 2, "IAB Category Score", bold)
    for i, iab_category in enumerate(data["iab_categories"]):
        worksheet_iab_categories.write(i + 1, 0, iab_category["id"])
        worksheet_iab_categories.write(i + 1, 1, iab_category["name"])
        worksheet_iab_categories.write(i + 1, 2, iab_category["score"])

    # close the workbook
    workbook.close()

def run_transcription(file_path, output_file_path):
    """
    Runs a transcription
    """
    # upload the file
    audio_url = upload_file(file_path)

    # get the transcript
    transcript_id = get_transcript(audio_url)

    # poll for completion
    data = poll(transcript_id)

    # create the spreadsheet
    create_spreadsheet(data, output_file_path)