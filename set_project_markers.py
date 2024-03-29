#!/usr/bin/env python3

import sys
import argparse
from typing import Dict
from typing import List

import pandas as pd
import pymiere

import utils


def main(argv):
    args = parse_args(argv)
    file = args.file
    transcript_data = pd.read_excel(file, sheet_name='chapters', index_col=None, header=0).transpose().to_dict().values()
    if transcript_data is None:
        print("unable to open json file", file=sys.stderr)
        return -1

    pymiere_proj, all_markers = utils.setup_pymiere()
    clear_markers(all_markers)
    insert_chapters(all_markers, transcript_data)

    return 0


def insert_chapters(all_markers: pymiere.MarkerCollection, chapters_list: List[Dict]):
    for chapter in chapters_list:
        cur_marker = all_markers.createMarker(utils.timecode_to_transcript_time(chapter["start"]))
        cur_marker.comments = chapter["gist"]
        print(f"Inserting marker: [{utils.transcript_time_to_timecode(cur_marker.start.seconds)} : {cur_marker.comments}]")


def clear_markers(all_markers: pymiere.MarkerCollection):
    if all_markers.numMarkers > 0:
        print(f"Clearing markers: {all_markers.numMarkers}")
        while all_markers.numMarkers > 0:
            marker = all_markers.getFirstMarker()
            all_markers.deleteMarker(marker)


def parse_args(argv):
    parser = argparse.ArgumentParser('Import transcript json and place markers in Premiere project')
    parser.add_argument("-f", "--file", help="File path to json")
    return parser.parse_args(args=argv)


if __name__ == '__main__':
    exit(main(sys.argv[1:]))
