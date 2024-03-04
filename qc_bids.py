# Yuncong Ma, 2/29/2024
# perform quality control on the bids formatted data


import os, sys, glob, argparse, subprocess, socket, operator, shutil, json, string, re
from bids import BIDSLayout
import numpy as np
import nibabel as nib


def generate_parser(parser=None):
    """
    Generates the command line parser for this program.
    :param parser: optional subparser for wrapping this program as a submodule.
    :return: ArgumentParser for this script/module
    """
    if not parser:
        parser = argparse.ArgumentParser(
            description='This function is to do qc on bids formatted data'
        )
    parser.add_argument(
        'dir_bids',
        help='path to the bids dataset root directory'
    )
    parser.add_argument(
        'dir_fsl',
        help="Required: Path to FSL directory"
    )
    parser.add_argument(
        'participant',
        help='Required: participant label'
    )
    parser.add_argument(
        'session',
        help='Required: session label'
    )

    parser.add_argument(
        '-o', '--dir_output', default='./QC/',
        help='Directory to store qc results'
    )

    return parser


def main(argv=sys.argv):
    parser = generate_parser()
    args = parser.parse_args()

    print('Start qc for bids')

    # compute spatial similarity between fmap and func after rigid-body alignment

    # check phase encoding direction between fmap and func

    # provides example graphs of all anat, func, fmap images

    # check potential artifacts between

    # generate an HTML-based report


if __name__ == "__main__":
    sys.exit(main())

