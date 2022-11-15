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
    Uploads a file to AssemblyAI
    """
    # open the file and get the file size
    with open(file_path, 'rb') as f:
        file_size = os.path.getsize(file_path)

        # upload the file in chunks
        upload_url = None
        chunk_num = 0
        while True:
            # get the chunk
            chunk = f.read(CHUNK_SIZE)

            # if we've reached the end of the file, break out of the loop
            if not chunk:
                break

            # get the upload url if we don't have one yet
            if not upload_url:
                upload_resp = requests.post(upload_endpoint, headers=headers_auth_only)
                upload_url = upload_resp.json()["upload_url"]

            # upload the chunk
            requests.put(upload_url, data=chunk)

            # increment the chunk number
            chunk_num += 1

            # print out the progress
            print(f"Uploaded {chunk_num * CHUNK_SIZE}/{file_size} bytes ({int(chunk_num * CHUNK_SIZE * 100 / file_size)}%)")

    # return the upload url
    return upload_url

# Create a function that requests a transcript from AssemblyAI

def request_transcript(upload_url):
    """
    Requests a transcript from AssemblyAI
    """
    # request the transcript
    data = {
        "audio_url": upload_url,
        "model": "default",
        "speaker_channels": "combined",
        "speaker_labels": True,
        "confidence_threshold": 0.5,
        "auto_highlights": True,
        "iab_categories": True,
        "auto_chapters": True,
        "entity_detection": True
    }
    transcript_resp = requests.post(transcript_endpoint, headers=headers, data=json.dumps(data))
    transcript_id = transcript_resp.json()["id"]

    # print out the transcript id
    print(f"Transcript ID: {transcript_id}")

    # return the transcript id
    return transcript_id

# Create a function that polls for a response from AssemblyAI

def poll_for_completion(transcript_id):
    """
    Polls for a transcript to be completed
    """
    # poll for the transcript to be completed
    while True:
        transcript_resp = requests.get(f"{transcript_endpoint}/{transcript_id}", headers=headers)
        transcript_status = transcript_resp.json()["status"]
        print(f"Transcript status: {transcript_status}")

        # if the transcript has completed, break out of the loop
        if transcript_status == "completed":
            break

        # sleep for a second
        time.sleep(1)

# Create a function that gets all of the JSON data and write it to multiple sheets in an Excel spreadsheet.

def get_transcript_data(transcript_id):
    """
    Gets the transcript data from AssemblyAI
    """
    # get the transcript data
    transcript_resp = requests.get(f"{transcript_endpoint}/{transcript_id}", headers=headers)
    transcript_data = transcript_resp.json()

    # return the transcript data
    return transcript_data

# Create a function that writes the transcript data to an Excel spreadsheet

def write_transcript_to_excel(transcript_data, file_path):
    """
    Writes the transcript data to an Excel spreadsheet
    """
    # create the Excel workbook
    workbook = xlsxwriter.Workbook(file_path)

    # create the summary sheet
    summary_sheet = workbook.add_worksheet("Summary")
    summary_sheet.write(0, 0, "Transcript ID")
    summary_sheet.write(0, 1, transcript_data["id"])
    summary_sheet.write(1, 0, "Transcript Status")
    summary_sheet.write(1, 1, transcript_data["status"])
    summary_sheet.write(2, 0, "Transcript Duration")
    summary_sheet.write(2, 1, transcript_data["duration"])
    summary_sheet.write(3, 0, "Transcript Text")
    summary_sheet.write(3, 1, transcript_data["text"])
    summary_sheet.write(4, 0, "Transcript Confidence")
    summary_sheet.write(4, 1, transcript_data["confidence"])
    summary_sheet.write(5, 0, "Transcript Word Count")
    summary_sheet.write(5, 1, transcript_data["word_count"])
    summary_sheet.write(6, 0, "Transcript Character Count")
    summary_sheet.write(6, 1, transcript_data["character_count"])
    summary_sheet.write(7, 0, "Transcript Processing Time")
    summary_sheet.write(7, 1, transcript_data["processing_time"])
    summary_sheet.write(8, 0, "Transcript Created At")
    summary_sheet.write(8, 1, transcript_data["created_at"])
    summary_sheet.write(9, 0, "Transcript Updated At")
    summary_sheet.write(9, 1, transcript_data["updated_at"])

    # create the speakers sheet
    speakers_sheet = workbook.add_worksheet("Speakers")
    speakers_sheet.write(0, 0, "Speaker ID")
    speakers_sheet.write(0, 1, "Speaker Channel")
    speakers_sheet.write(0, 2, "Speaker Start Time")
    speakers_sheet.write(0, 3, "Speaker End Time")
    speakers_sheet.write(0, 4, "Speaker Duration")
    speakers_sheet.write(0, 5, "Speaker Text")
    speakers_sheet.write(0, 6, "Speaker Confidence")
    speakers_sheet.write(0, 7, "Speaker Word Count")
    speakers_sheet.write(0, 8, "Speaker Character Count")
    for i, speaker in enumerate(transcript_data["speakers"]):
        speakers_sheet.write(i + 1, 0, speaker["id"])
        speakers_sheet.write(i + 1, 1, speaker["channel"])
        speakers_sheet.write(i + 1, 2, speaker["start_time"])
        speakers_sheet.write(i + 1, 3, speaker["end_time"])
        speakers_sheet.write(i + 1, 4, speaker["duration"])
        speakers_sheet.write(i + 1, 5, speaker["text"])
        speakers_sheet.write(i + 1, 6, speaker["confidence"])
        speakers_sheet.write(i + 1, 7, speaker["word_count"])
        speakers_sheet.write(i + 1, 8, speaker["character_count"])

    # create the words sheet
    words_sheet = workbook.add_worksheet("Words")
    words_sheet.write(0, 0, "Word ID")
    words_sheet.write(0, 1, "Word Start Time")
    words_sheet.write(0, 2, "Word End Time")
    words_sheet.write(0, 3, "Word Duration")
    words_sheet.write(0, 4, "Word Text")
    words_sheet.write(0, 5, "Word Confidence")
    words_sheet.write(0, 6, "Word Speaker ID")
    for i, word in enumerate(transcript_data["words"]):
        words_sheet.write(i + 1, 0, word["id"])
        words_sheet.write(i + 1, 1, word["start_time"])
        words_sheet.write(i + 1, 2, word["end_time"])
        words_sheet.write(i + 1, 3, word["duration"])
        words_sheet.write(i + 1, 4, word["text"])
        words_sheet.write(i + 1, 5, word["confidence"])
        words_sheet.write(i + 1, 6, word["speaker_id"])

    # create the highlights sheet
    highlights_sheet = workbook.add_worksheet("Highlights")
    highlights_sheet.write(0, 0, "Highlight ID")
    highlights_sheet.write(0, 1, "Highlight Start Time")
    highlights_sheet.write(0, 2, "Highlight End Time")
    highlights_sheet.write(0, 3, "Highlight Duration")
    highlights_sheet.write(0, 4, "Highlight Text")
    highlights_sheet.write(0, 5, "Highlight Confidence")
    highlights_sheet.write(0, 6, "Highlight Speaker ID")
    for i, highlight in enumerate(transcript_data["highlights"]):
        highlights_sheet.write(i + 1, 0, highlight["id"])
        highlights_sheet.write(i + 1, 1, highlight["start_time"])
        highlights_sheet.write(i + 1, 2, highlight["end_time"])
        highlights_sheet.write(i + 1, 3, highlight["duration"])
        highlights_sheet.write(i + 1, 4, highlight["text"])
        highlights_sheet.write(i + 1, 5, highlight["confidence"])
        highlights_sheet.write(i + 1, 6, highlight["speaker_id"])

    # create the chapters sheet
    chapters_sheet = workbook.add_worksheet("Chapters")
    chapters_sheet.write(0, 0, "Chapter ID")
    chapters_sheet.write(0, 1, "Chapter Start Time")
    chapters_sheet.write(0, 2, "Chapter End Time")
    chapters_sheet.write(0, 3, "Chapter Duration")
    chapters_sheet.write(0, 4, "Chapter Text")
    chapters_sheet.write(0, 5, "Chapter Confidence")
    chapters_sheet.write(0, 6, "Chapter Speaker ID")
    for i, chapter in enumerate(transcript_data["chapters"]):
        chapters_sheet.write(i + 1, 0, chapter["id"])
        chapters_sheet.write(i + 1, 1, chapter["start_time"])
        chapters_sheet.write(i + 1, 2, chapter["end_time"])
        chapters_sheet.write(i + 1, 3, chapter["duration"])
        chapters_sheet.write(i + 1, 4, chapter["text"])
        chapters_sheet.write(i + 1, 5, chapter["confidence"])
        chapters_sheet.write(i + 1, 6, chapter["speaker_id"])

    # create the entities sheet
    entities_sheet = workbook.add_worksheet("Entities")
    entities_sheet.write(0, 0, "Entity ID")
    entities_sheet.write(0, 1, "Entity Start Time")
    entities_sheet.write(0, 2, "Entity End Time")
    entities_sheet.write(0, 3, "Entity Duration")
    entities_sheet.write(0, 4, "Entity Text")
    entities_sheet.write(0, 5, "Entity Confidence")
    entities_sheet.write(0, 6, "Entity Speaker ID")
    entities_sheet.write(0, 7, "Entity Type")
    entities_sheet.write(0, 8, "Entity Subtype")
    for i, entity in enumerate(transcript_data["entities"]):
        entities_sheet.write(i + 1, 0, entity["id"])
        entities_sheet.write(i + 1, 1, entity["start_time"])
        entities_sheet.write(i + 1, 2, entity["end_time"])
        entities_sheet.write(i + 1, 3, entity["duration"])
        entities_sheet.write(i + 1, 4, entity["text"])
        entities_sheet.write(i + 1, 5, entity["confidence"])
        entities_sheet.write(i + 1, 6, entity["speaker_id"])
        entities_sheet.write(i + 1, 7, entity["type"])
        entities_sheet.write(i + 1, 8, entity["subtype"])

    # create the iab_categories sheet
    iab_categories_sheet = workbook.add_worksheet("IAB Categories")
    iab_categories_sheet.write(0, 0, "IAB Category ID")
    iab_categories_sheet.write(0, 1, "IAB Category Name")
    iab_categories_sheet.write(0, 2, "IAB Category Confidence")
    for i, iab_category in enumerate(transcript_data["iab_categories"]):
        iab_categories_sheet.write(i + 1, 0, iab_category["id"])
        iab_categories_sheet.write(i + 1, 1, iab_category["name"])
        iab_categories_sheet.write(i + 1, 2, iab_category["confidence"])

    # close the workbook
    workbook.close()

# Create a function that runs the entire process

def run_transcription(file_path, output_file_path):
    """
    Runs the transcription process
    """
    # upload the file
    print("Uploading file...")
    upload_url = upload_file(file_path)
    print("Upload complete!")

    # request a transcript
    print("Requesting transcript...")
    transcript_id = request_transcript(upload_url)
    print("Transcript requested!")

    # poll for completion
    print("Polling for completion...")
    poll_for_completion(transcript_id)
    print("Transcript complete!")

    # get the transcript data
    print("Getting transcript data...")
    transcript_data = get_transcript_data(transcript_id)
    print("Transcript data received!")

    # write the transcript data to an Excel spreadsheet
    print("Writing transcript data to Excel...")
    write_transcript_to_excel(transcript_data, output_file_path)
    print("Transcript data written to Excel!")

# Create a function that runs the entire process

def run_transcription(file_path, output_file_path):
    """
    Runs the transcription process
    """
    # upload the file
    print("Uploading file...")
    upload_url = upload_file(file_path)
    print("Upload complete!")

    # request a transcript
    print("Requesting transcript...")
    transcript_id = request_transcript(upload_url)
    print("Transcript requested!")

    # poll for completion
    print("Polling for completion...")
    poll_for_completion(transcript_id)
    print("Transcript complete!")

    # get the transcript data
    print("Getting transcript data...")
    transcript_data = get_transcript_data(transcript_id)
    print("Transcript data received!")

    # write the transcript data to an Excel spreadsheet
    print("Writing transcript data to Excel...")
    write_transcript_to_excel(transcript_data, output_file_path)
    print("Transcript data written to Excel!")