#! /usr/bin/env python3
# Yuncong Ma, 4/3/2024
# Convert manual BIDS QC file to BIDS filter file

import os, sys, argparse, re, json, shutil
from bids import BIDSLayout
import numpy as np
from Data_Input import write_json_setting


def remove_json_field(json_path, json_field):

    with open(json_path, 'r+') as f:
        data = json.load(f)

        if json_field in data:
            del data[json_field]
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
            flag = True
        else:
            flag = False

    return flag


def update_json_field(json_path, json_field, value):

    with open(json_path, 'r+') as f:
        data = json.load(f)

        if json_field in data:
            flag = True
        else:
            flag = False

        data[json_field] = value
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

    return flag


def generate_parser(parser=None):
    """
    Generates the command line parser for this program.
    :param parser: optional subparser for wrapping this program as a submodule.
    :return: ArgumentParser for this script/module
    """
    if not parser:
        parser = argparse.ArgumentParser(
            description='bids_filter is to convert manual BIDS QC file to BIDS filter file'
        )
    parser.add_argument(
        '--bids', dest='dir_bids',
        help='path to the BIDS folder.'
    )
    parser.add_argument(
        '--bids-qc', dest='dir_bids_qc',
        help='path to the BIDS_QC folder.'
    )
    parser.add_argument(
        '--fmriprep-work', dest='dir_fmriprep_work',
        help='path to the fmriprep_work folder.'
    )
    parser.add_argument(
        '--sub', dest='subject',
        help='subject info'
    )
    parser.add_argument(
        '--ses', dest='session',
        help='session info'
    )

    return parser


def find_file(file_name, search_dir):
    """
    Searches for a file within a directory and its subdirectories.

    Parameters:
    file_name (str): The name of the file to search for.
    search_dir (str): The directory to search in.

    Returns:
    str: The full path to the file if found, otherwise None.
    """
    for dirpath, dirnames, filenames in os.walk(search_dir):
        if file_name in filenames:
            # File found, return the full path
            return os.path.join(dirpath, file_name)
    # If the loop completes without finding the file, return None
    raise ValueError("Cannot find the "+file_name + " in "+search_dir)


def main(argv=sys.argv):
    parser = generate_parser()
    args = parser.parse_args()

    print('Start bids_filter')

    subject = args.subject
    session = args.session

    folder_label = "sub-" + args.subject + "_ses-" + args.session

    file_bids_qc = os.path.join(args.dir_bids_qc, folder_label+'.txt')

    dir_bids_sub = os.path.join(args.dir_bids, "sub-" + args.subject, "ses-" + args.session)
    dir_fmriprep_work_sub = os.path.join(args.dir_fmriprep_work, folder_label)
    dir_fmriprep_work_sub_bids = os.path.join(dir_fmriprep_work_sub, 'BIDS')
    dir_fmriprep_work_sub_bids_inner = os.path.join(dir_fmriprep_work_sub_bids, "sub-" + args.subject, "ses-" + args.session)

    # make directories
    if not os.path.exists(dir_fmriprep_work_sub):
        os.makedirs(dir_fmriprep_work_sub)
    if not os.path.exists(dir_fmriprep_work_sub_bids):
        os.makedirs(dir_fmriprep_work_sub_bids)
        os.makedirs(dir_fmriprep_work_sub_bids_inner)
        os.makedirs(os.path.join(dir_fmriprep_work_sub_bids_inner, 'anat'))
        os.makedirs(os.path.join(dir_fmriprep_work_sub_bids_inner, 'func'))
        os.makedirs(os.path.join(dir_fmriprep_work_sub_bids_inner, 'fmap'))

    # start to copy files from BIDS to fmriprep_work
    shutil.copy(os.path.join(args.dir_bids, 'dataset_description.json'), os.path.join(dir_fmriprep_work_sub_bids, 'dataset_description.json'))
    with open(file_bids_qc) as file:
        for line in file.readlines():
            if len(line) > 2:
                file_mri_name, status_mri = str.split(line, ': ')
                if status_mri == 'pass\n':
                    file_bids_mri = find_file(file_mri_name, dir_bids_sub)
                    name_tag = str.split(file_bids_mri, '/')
                    # print('copy '+file_bids_mri+' : '+os.path.join(dir_fmriprep_work_sub_bids_inner, name_tag[-2]))
                    shutil.copy(file_bids_mri, os.path.join(dir_fmriprep_work_sub_bids_inner, name_tag[-2]))
                    shutil.copy(file_bids_mri.replace('.nii.gz', '.json'), os.path.join(dir_fmriprep_work_sub_bids_inner, name_tag[-2]))

    # new bids
    layout = BIDSLayout(dir_fmriprep_work_sub_bids, is_derivative=True)

    # Add metadata
    func_list = [os.path.join(x.dirname.replace(dir_fmriprep_work_sub_bids, '.'), x.filename).replace('./sub-'+args.subject+'/', '') for x in layout.get(subject=subject, session=session, datatype='func', extension='.nii.gz')]
    anat_list = [os.path.join(x.dirname.replace(dir_fmriprep_work_sub_bids, '.'), x.filename).replace('./sub-'+args.subject+'/', '') for x in layout.get(subject=subject, session=session, datatype='anat', extension='.nii.gz')]
    
    print('Add meta data in keyword IntendedFor')
    print(func_list)
    print(anat_list)

    # update IntendedFor in all field maps

    list_fmap_AP = layout.get(subject=subject, session=session, datatype='fmap', extension='.nii.gz')
    for file_fmap in [os.path.join(x.dirname, x.filename) for x in list_fmap_AP]:
        print('Add IntendedFor for field map: '+file_fmap.replace('.nii.gz', '.json').replace(dir_fmriprep_work_sub_bids, '.'))
        update_json_field(file_fmap.replace('.nii.gz', '.json'), 'IntendedFor', anat_list + func_list)

    print('Finish bids_filter')


if __name__ == "__main__":
    sys.exit(main())
