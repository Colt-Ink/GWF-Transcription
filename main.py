# main.py:

import requests
import os
import time
import xlsxwriter
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
    return upload_response.json()

# Get transcript

def get_transcript(audio_url):
    """
    Gets a transcript from AssemblyAI
    """
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
    transcript_response = requests.post(
        transcript_endpoint,
        headers=headers,
        json=data
    )
    return transcript_response.json()['id']

# Poll for transcript

def poll_for_transcript(transcript_id):
    """
    Polls AssemblyAI for a transcript
    """
    while True:
        transcript_response = requests.get(
            transcript_endpoint + "/" + transcript_id,
            headers=headers
        )
        transcript_response_json = transcript_response.json()
        if transcript_response_json["status"] == "completed":
            return transcript_response_json
        elif transcript_response_json["status"] == "failed":
            return transcript_response_json['error']
        else:
            from run import start_time
            time.sleep(30)
            print("Checking again in 30 secs")
            print("Elapsed time:", time.time() - start_time)

# Write transcript to Excel

def write_transcript_to_excel(transcript_json, excel_file_path):
    """
    Writes a transcript to an Excel file
    """
    workbook = xlsxwriter.Workbook(excel_file_path)
    worksheet_words = workbook.add_worksheet("words")
    worksheet_speakers = workbook.add_worksheet("speakers")
    worksheet_highlights = workbook.add_worksheet("highlights")
    worksheet_chapters = workbook.add_worksheet("chapters")
    worksheet_entities = workbook.add_worksheet("entities")
    worksheet_iab_categories = workbook.add_worksheet("iab_categories")

    # Write words
    worksheet_words.write(0, 0, "start_time")
    worksheet_words.write(0, 1, "end_time")
    worksheet_words.write(0, 2, "confidence")
    worksheet_words.write(0, 3, "speaker_label")
    worksheet_words.write(0, 4, "word")
    row = 1
    for word in transcript_json["words"]:
        worksheet_words.write(row, 0, word["start_time"])
        worksheet_words.write(row, 1, word["end_time"])
        worksheet_words.write(row, 2, word["confidence"])
        worksheet_words.write(row, 3, word["speaker_label"])
        worksheet_words.write(row, 4, word["word"])
        row += 1

    # Write speakers
    worksheet_speakers.write(0, 0, "speaker_label")
    worksheet_speakers.write(0, 1, "start_time")
    worksheet_speakers.write(0, 2, "end_time")
    row = 1
    for speaker in transcript_json["speakers"]:
        worksheet_speakers.write(row, 0, speaker["speaker_label"])
        worksheet_speakers.write(row, 1, speaker["start_time"])
        worksheet_speakers.write(row, 2, speaker["end_time"])
        row += 1

    # Write highlights
    worksheet_highlights.write(0, 0, "start_time")
    worksheet_highlights.write(0, 1, "end_time")
    worksheet_highlights.write(0, 2, "text")
    row = 1
    for highlight in transcript_json["highlights"]:
        worksheet_highlights.write(row, 0, highlight["start_time"])
        worksheet_highlights.write(row, 1, highlight["end_time"])
        worksheet_highlights.write(row, 2, highlight["text"])
        row += 1

    # Write chapters
    worksheet_chapters.write(0, 0, "start_time")
    worksheet_chapters.write(0, 1, "end_time")
    worksheet_chapters.write(0, 2, "text")
    row = 1
    for chapter in transcript_json["chapters"]:
        worksheet_chapters.write(row, 0, chapter["start_time"])
        worksheet_chapters.write(row, 1, chapter["end_time"])
        worksheet_chapters.write(row, 2, chapter["text"])
        row += 1

    # Write entities
    worksheet_entities.write(0, 0, "start_time")
    worksheet_entities.write(0, 1, "end_time")
    worksheet_entities.write(0, 2, "text")
    worksheet_entities.write(0, 3, "entity")
    row = 1
    for entity in transcript_json["entities"]:
        worksheet_entities.write(row, 0, entity["start_time"])
        worksheet_entities.write(row, 1, entity["end_time"])
        worksheet_entities.write(row, 2, entity["text"])
        worksheet_entities.write(row, 3, entity["entity"])
        row += 1

    # Write IAB categories
    worksheet_iab_categories.write(0, 0, "start_time")
    worksheet_iab_categories.write(0, 1, "end_time")
    worksheet_iab_categories.write(0, 2, "text")
    worksheet_iab_categories.write(0, 3, "iab_category")
    row = 1
    for iab_category in transcript_json["iab_categories"]:
        worksheet_iab_categories.write(row, 0, iab_category["start_time"])
        worksheet_iab_categories.write(row, 1, iab_category["end_time"])
        worksheet_iab_categories.write(row, 2, iab_category["text"])
        worksheet_iab_categories.write(row, 3, iab_category["iab_category"])
        row += 1

    workbook.close()

# Run transcription

def run_transcription(file_path, title):
    """
    Runs a transcription
    """
    # Upload the file
    upload_response_json = upload_file(file_path)
    audio_url = upload_response_json["audio_url"]

    # Get the transcript
    transcript_response_json = get_transcript(audio_url)
    transcript_id = transcript_response_json["id"]

    # Poll for the transcript
    transcript_json = poll_for_transcript(transcript_id)

    # Write the transcript to Excel
    write_transcript_to_excel(transcript_json, f"{title}.xlsx")