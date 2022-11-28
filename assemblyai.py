import os
import time

import requests
from tqdm import tqdm

from api_secrets import API_KEY_ASSEMBLYAI

upload_endpoint = "https://api.assemblyai.com/v2/upload"
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"

headers_auth_only = {'authorization': API_KEY_ASSEMBLYAI}

headers_json = {
    "authorization": API_KEY_ASSEMBLYAI,
    "content-type": "application/json"
}

CHUNK_SIZE = 5_242_880  # 5MB


def upload_file(file_path):
    """
    Uploads a file to AssemblyAI with a progress bar
    """

    def read_file_with_progress(file_path):
        with open(file_path, "rb") as f:
            with tqdm(total=os.path.getsize(file_path),
                      unit="B", unit_scale=True, unit_divisor=1024
                      ) as t:

                while True:
                    data = f.read(CHUNK_SIZE)
                    if not data:
                        break
                    t.update(len(data))
                    yield data

    upload_response = requests.post(
        upload_endpoint,
        headers=headers_auth_only,
        data=read_file_with_progress(file_path)
    )
    return upload_response.json()


def get_transcript(audio_url, data):
    """
    Gets a transcript from AssemblyAI
    """
    data["audio_url"] = audio_url
    transcript_response = requests.post(
        transcript_endpoint,
        headers=headers_json,
        json=data
    )
    return transcript_response.json()


def poll_for_transcript(transcript_id):
    """
    Polls AssemblyAI for a transcript
    """
    start_time = time.time()
    while True:
        transcript_response = requests.get(
            transcript_endpoint + "/" + transcript_id,
            headers=headers_json
        )
        transcript_response_json = transcript_response.json()
        if transcript_response_json["status"] == "completed":
            return transcript_response_json
        elif transcript_response_json["status"] == "failed":
            print(transcript_response_json)
            raise Exception(transcript_response_json['error'])
        elif transcript_response_json["status"] == "error":
            print(transcript_response_json)
            raise Exception(transcript_response_json['error'])
        else:
            time.sleep(30)
            print("Checking again in 30 secs")
            print("Elapsed time:", time.time() - start_time)


def get_srt(transcript_id):
    response = requests.get(f"{transcript_endpoint}/{transcript_id}/srt", headers=headers_auth_only)
    return response.text


def get_paragraphs(transcript_id):
    paragraphs_response = requests.get(f"{transcript_endpoint}/{transcript_id}/paragraphs", headers=headers_json)
    paragraphs_response = paragraphs_response.json()

    paragraphs = []
    for para in paragraphs_response['paragraphs']:
        paragraphs.append(para)

    return paragraphs
