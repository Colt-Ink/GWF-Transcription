#!/usr/bin/env python3
import sys
import argparse

import utils


def main(argv):
    args = parse_args(argv)
    pymiere_proj, all_markers = utils.setup_pymiere()
    tempAudio, result = utils.extract_project_audio(pymiere_proj)
    print(result)
    print(tempAudio)
    return 0


def parse_args(argv):
    parser = argparse.ArgumentParser('Export audio from active premiere sequence')
    return parser.parse_args(args=argv)


if __name__ == '__main__':
    exit(main(sys.argv[1:]))
