#! /usr/bin/env python3
# Yuncong Ma, 3/7/2024
# Correct information in BIDs formatted data generated using unpack_and_setup_yuncong.sh
# adapted from abcd_dicom2bids/src/correct_json.py

import argparse
import glob
import json
import os
import sys
import re


def read_json_field(json_path, json_field):

    with open(json_path, 'r') as f:
        data = json.load(f)

    if json_field in data:
        return data[json_field]
    else:
        return None


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


def main(argv=None):
    if argv is None:
        argv = sys.argv
    parser = argparse.ArgumentParser(
        prog='correct_jsons.py',
        description='correct json files in BIDS folder',
        usage='%(prog)s --bids --subject --session'
    )
    parser.add_argument(
        '-bids',
        help='Path to the input BIDS dataset root directory.  Read more '
             'about the BIDS standard in the link in the description.  It is '
             'recommended to use Dcm2Bids to convert from participant dicoms '
             'into BIDS format.'
    )
    parser.add_argument(
        '-subject',
        help='subject name without sub-'
    )
    parser.add_argument(
        '-session',
        help='session name without ses-'
    )

    args = parser.parse_args()

    flag_correction = 0
    for root, dirs, files in os.walk(os.path.join(args.bids, 'sub-'+args.subject, 'ses-'+args.session)):
        for filename in files:
            fn, ext = os.path.splitext(filename)

            if ext == '.json':
                json_path = os.path.join(root, filename)

                with open(json_path, 'r') as f:
                    data = json.load(f)

                # If TotalReadoutTime is missing from fmap JSON
                if ('fmap' in root or 'func' in root) and 'TotalReadoutTime' not in data:
                    # Then check for EffectiveEchoSpacing and ReconMatrixPE

                    if 'EffectiveEchoSpacing' in data and 'ReconMatrixPE' in data:
                        flag_correction += 1
                        # If both are present then update the JSON with a calculated TotalReadoutTime
                        EffectiveEchoSpacing = data['EffectiveEchoSpacing']
                        ReconMatrixPE = data['ReconMatrixPE']
                        # Calculated TotalReadoutTime = EffectiveEchoSpacing * (ReconMatrixPE - 1)
                        TotalReadoutTime = EffectiveEchoSpacing * (ReconMatrixPE - 1)
                        update_json_field(json_path, 'TotalReadoutTime', TotalReadoutTime)

                    # If EffectiveEchoSpacing is missing print error
                    if 'EffectiveEchoSpacing' not in data:
                        flag_correction += 1
                        print(json_path + ': No EffectiveEchoSpacing')

                    # If ReconMatrixPE is missing print error
                    if 'ReconMatrixPE' not in data:
                        flag_correction += 1
                        print(json_path + ': No ReconMatrixPE')

                # skip this step due to updated code in sefm_eval_and_json_editor_yuncong.py
                # Find the IntendedFor field that is a non-empty list
                # if 'fmap' in root and 'IntendedFor' in data and len(data['IntendedFor']) > 0:
                #     # Regular expression replace all paths in that list with a relative path to ses-SESSION
                #     intended_list = data['IntendedFor']
                #     corrected_intended_list = [re.sub(r'.*(ses-.*_ses-.+)','\g<1>',entry) for entry in intended_list]
                #     update_json_field(json_path, 'IntendedFor', corrected_intended_list)

                # add SliceTiming in func JSONs
                if 'func' in root and 'SliceTiming' not in data:
                    flag_correction += 1
                    print('insert default SliceTiming into func json files')
                    slice_timing_default = [0.545,
                                            0,
                                            0.39,
                                            0.0775,
                                            0.4675,
                                            0.2325,
                                            0.6225,
                                            0.31,
                                            0.7,
                                            0.155,
                                            0.545,
                                            0,
                                            0.39,
                                            0.0775,
                                            0.4675,
                                            0.2325,
                                            0.6225,
                                            0.31,
                                            0.7,
                                            0.155,
                                            0.545,
                                            0,
                                            0.39,
                                            0.0775,
                                            0.4675,
                                            0.2325,
                                            0.6225,
                                            0.31,
                                            0.7,
                                            0.155,
                                            0.545,
                                            0,
                                            0.39,
                                            0.0775,
                                            0.4675,
                                            0.2325,
                                            0.6225,
                                            0.31,
                                            0.7,
                                            0.155,
                                            0.545,
                                            0,
                                            0.39,
                                            0.0775,
                                            0.4675,
                                            0.2325,
                                            0.6225,
                                            0.31,
                                            0.7,
                                            0.155,
                                            0.545,
                                            0,
                                            0.39,
                                            0.0775,
                                            0.4675,
                                            0.2325,
                                            0.6225,
                                            0.31,
                                            0.7,
                                            0.155
                                          ]
                    update_json_field(json_path, 'SliceTiming', slice_timing_default)

    sub_dirs = os.path.join(args.bids, 'sub-'+args.subject, 'ses-'+args.session)
    for json_path in glob.iglob(os.path.join(sub_dirs, "*.json")):
        print("Removing .JSON file: {}".format(json_path))
        os.remove(json_path)
        flag_correction += 1
    for vol_file in glob.iglob(os.path.join(sub_dirs, "fmap", "vol*.nii.gz")):
        print("Removing 'vol' file: {}".format(vol_file))
        os.remove(vol_file)
        flag_correction += 1

    if flag_correction > 0:
        print('\n'+str(flag_correction)+' corrections were performed for json files.\n')
    else:
        print('\nNo correction is needed for all the json files.\n')


if __name__ == "__main__":
    sys.exit(main())
