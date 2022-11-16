from setuptools import setup

setup(
    name="GWF-Transcription",
    version="1.0.0",
    description="Transcribe a file with AssemblyAI",
    author="Colt Peterson",
    author_email="colt@colt.ink",
    url="https://github.com/Colt-Ink/GWF-Transcription",
    packages=["GWF-Transcription"],
    install_requires=[
        "requests",
        "xlsxwriter",
        "tqdm"
    ],
    entry_points={
        "console_scripts": [
            "assemblyai-transcribe = assemblyai-transcribe.run:main"
        ]
    }
)