import os
import tempfile

import pymiere
from pymiere import wrappers
from timecode import Timecode


def transcript_time_to_timecode(transcript_time):
    hours, milliseconds = divmod(transcript_time, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    seconds = float(milliseconds) / 1000
    return '{:02}:{:02}:{:06.3f}'.format(int(hours), int(minutes), seconds)


def timecode_to_transcript_time(timecode: str):
    tc = Timecode('ms', timecode)
    return tc.float


def setup_pymiere() -> (pymiere.Application, pymiere.MarkerCollection):
    project_opened, sequence_active = wrappers.check_active_sequence(crash=False)
    if not project_opened:
        raise ValueError("please open a project")
    project = pymiere.objects.app.project
    if not sequence_active:
        sequences = wrappers.list_sequences()
        for seq in sequences:
            project.openSequence(sequenceID=seq.sequenceID)
        # Set the first Sequence in the list as the active Sequence
        project.activeSequence = sequences[0]

    return project, project.activeSequence.markers


def extract_project_audio(pymiere_proj):
    tempdir = tempfile.mkdtemp()
    tempFile = os.path.join(tempdir, "out.wav")
    preset_path = os.path.abspath(os.path.join(os.getcwd(), "encoder_presets", "ExtractRawAudio.epr"))
    result = pymiere_proj.activeSequence.exportAsMediaDirect(tempFile, preset_path,
                                                             pymiere.objects.app.encoder.ENCODE_IN_TO_OUT)
    return tempFile, result
