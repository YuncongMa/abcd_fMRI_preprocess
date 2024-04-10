#! /usr/bin/env python3
# Yuncong Ma, 4/4/2024
# Use manual QC files to update figures in BIDS_QC report
# Failed MRI images will show red borders, while passed ones will show green borders.
# It works directly in the BIDS_QC folder for all available reports

import os, sys, argparse, re, subprocess
from bids import BIDSLayout
import numpy as np

def generate_parser(parser=None):
    """
    Generates the command line parser for this program.
    :param parser: optional subparser for wrapping this program as a submodule.
    :return: ArgumentParser for this script/module
    """
    if not parser:
        parser = argparse.ArgumentParser(
            description='It is to update figures in BIDS_QC report'
        )
    parser.add_argument(
        '--bids-qc', dest='dir_bids_qc',
        help="directory of BIDS_QC"
    )

    return parser


def main(argv=sys.argv):
    parser = generate_parser()
    args = parser.parse_args()

    print('Start updating BIDS_QC')

    dir_bids_qc = args.dir_bids_qc

    # find all html report
    list_report = []
    for root, dirs, files in os.walk(dir_bids_qc):
        for filename in files:
            if filename.endswith(".html"):
                Keywords = filename.split('_')
                subject = Keywords[0]
                session = Keywords[1]
                list_report.append(os.path.join(dir_bids_qc, filename))

    print('Finish updating BIDS_QC')


if __name__ == "__main__":
    sys.exit(main())
