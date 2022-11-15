from setuptools import setup

setup(
    name="assemblyai-transcribe",
    version="1.0.0",
    description="Transcribe a file with AssemblyAI",
    author="Colt Peterson",
    author_email="colt@colt.ink",
    url="",
    packages=["assemblyai-transcribe"],
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
