#!/usr/bin/env python3
import json
import sys
import argparse

import pymiere
from pymiere import wrappers


def main(argv):
    args = parse_args(argv)
    file = args.file
    transcript_data = None
    with open(file, 'r') as openfile:
        transcript_data = json.load(openfile)
    if transcript_data is None:
        print("unable to open json file", file=sys.stderr)
        return -1

    pymiere_proj, all_markers = setup_pymiere()
    print(f"Number of markers: {all_markers.numMarkers}")

    # Iterate through all chapters in transcript_data
    for chapter in transcript_data["chapters"]:
        curMarker = all_markers.createMarker(float(chapter["start"]))
        curMarker.comments = chapter["gist"]

    return 0


def setup_pymiere() -> (pymiere.Application, pymiere.MarkerCollection):
    # Check for an open project
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


def parse_args(argv):
    parser = argparse.ArgumentParser('Import transcript json and place markers in Premiere project')
    parser.add_argument("-f", "--file", help="File path to json")
    return parser.parse_args(args=argv)


if __name__ == '__main__':
    exit(main(sys.argv[1:]))
