#!/usr/bin/env python3

import sys
import argparse

import pymiere
from pymiere import wrappers
import pandas as pd

import utils


def main(argv):
    args = parse_args(argv)
    file = args.file
    transcript_data = pd.read_excel(file, sheet_name='chapters', index_col=None, header=0).transpose().to_dict()
    if transcript_data is None:
        print("unable to open json file", file=sys.stderr)
        return -1

    pymiere_proj, all_markers = setup_pymiere()
    clear_markers(all_markers)
    # Iterate through all chapters in transcript_data
    for chapter in transcript_data.values():
        curMarker = all_markers.createMarker(utils.timecode_to_transcript_time(chapter["start"]))
        curMarker.comments = chapter["gist"]
        print(f"Inserting marker: [{utils.transcript_time_to_timecode(curMarker.start.seconds)} : {curMarker.comments}]")

    return 0


def clear_markers(all_markers):
    if all_markers.numMarkers > 0:
        print(f"Clearing markers: {all_markers.numMarkers}")
        marker = all_markers.getFirstMarker()
        while marker is not None:
            all_markers.deleteMarker(marker)
            if all_markers.numMarkers > 0:
                marker = all_markers.getFirstMarker()
            else:
                marker = None


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
