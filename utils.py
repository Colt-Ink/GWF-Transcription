
from timecode import Timecode


def transcript_time_to_timecode(transcript_time):
    hours, milliseconds = divmod(transcript_time, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    seconds = float(milliseconds) / 1000
    return '{:02}:{:02}:{:06.3f}'.format(int(hours), int(minutes), seconds)


def timecode_to_transcript_time(timecode: str):
    tc = Timecode('ms', timecode)
    return tc.float