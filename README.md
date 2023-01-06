# Introduction

The purpose of this project is to use audio intelligence from the Assembly AI API to helps automate some video editing tasks. Example uses might include generation of dialogue-driven rough cuts in Premiere Pro, simplification of metadata tagging (dublin core, YouTube chapters) to improve delivery, and (possibly) weakly-guided vertical reframing using diarization.

A powerful way to do this (and more) is to use "Pymiere" ([1] https://github.com/qmasingarbe/pymiere) along with Assembly AI data.  Furthermore, we can use a Youtube-Uploader like ([2] https://github.com/porjo/youtubeuploader) to package up the output and deliver it to YouTube via the YouTube DATA API. 

# Assembly AI Transcribe

Transcribe a file with AssemblyAI straight out of a Premiere project, return chapter markers to the timeline.

It operates with the following steps:

1. Extract Audio
2. Upload/get transcript
3. Insert markers  

# Installation   

copy scripts, run python premiere_stages.py with preferred options


# Usage

## Create a virtual environment in the project directory:

    python3 -m venv ./venv
    

## Activate `venv`:

    | Platform | Shell      | Command                                 |
    | -------- | ---------- | --------------------------------------- |
    | POSIX    | bash/zsh   | `source _<venv>_/bin/activate`          |
    | POSIX    | fish       | `source _<venv>_/bin/activate.fish`     |
    | POSIX    | csh/tcsh   | `source _<venv>_/bin/activate.csh`      |
    | POSIX    | PowerShell | `_<venv>_/bin/Activate.ps1`             |
    | Windows  | cmd.exe    | `C:\> _<venv>_\Scripts\activate.bat`    |
    | Windows  | PowerShell | `PS C:\> _<venv>_\Scripts\Activate.ps1` |

## Install `requirements.txt`

In the activated `venv`:

    pip install -r requirements.txt OR py -m pip install -r requirements.txt

## Run script:


    python premiere_stages.py -f <file_path> -s 1 2 3

# Examples

```
python main.py -f "G:\My Drive\GWF\2022\0040_GWF_Pod_500_AlissaBennett\0040-001_GWF_Pod_500_alissaBennett_FULL-EP\WORKING\LINKS\AUDIO\TREATED_alissaBennett_INTERVIEW.wav" -t "Alissa Bennett Interview"
```

# Notes

If you already have the transcribed audio, you can use the --id arg to avoid reprocessing everything on AssemblyAI.
If you already have an xlsx file, you can use --xlsx arg to point directly to a usable xlsx file.

Right now, all produced output of the wav and xlsx are stored in the system temp files. This makes it a little bit of a pain to get to if you really want them. Something to work on next.