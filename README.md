# AssemblyAI Transcribe

Transcribe a file with AssemblyAI

## Installation

```
copy scripts, run python main.py
```

## Usage
In the project directory
```bash
python3 -m venv ./venv
```
Activate `venv`:

| Platform | Shell      | Command                                 |
| -------- | ---------- | --------------------------------------- |
| POSIX    | bash/zsh   | `source _<venv>_/bin/activate`          |
| POSIX    | fish       | `source _<venv>_/bin/activate.fish`     |
| POSIX    | csh/tcsh   | `source _<venv>_/bin/activate.csh`      |
| POSIX    | PowerShell | `_<venv>_/bin/Activate.ps1`             |
| Windows  | cmd.exe    | `C:\> _<venv>_\Scripts\activate.bat`    |
| Windows  | PowerShell | `PS C:\> _<venv>_\Scripts\Activate.ps1` |

Install `requirements.txt`

In the activated `venv`:
```bash
pip install -r requirements.txt
```

```
assemblyai-transcribe -f <file_path> -t <title>
```

## Example

```
assemblyai-transcribe -f "G:\My Drive\GWF\2022\0040_GWF_Pod_500_AlissaBennett\0040-001_GWF_Pod_500_alissaBennett_FULL-EP\WORKING\LINKS\AUDIO\TREATED_alissaBennett_INTERVIEW.wav" -t "Alissa Bennett Interview"
```
