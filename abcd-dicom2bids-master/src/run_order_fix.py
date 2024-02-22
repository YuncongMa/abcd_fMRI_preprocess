#!/usr/bin/env python3
import argparse
import datetime
import json
import os
import re
import shutil
import tempfile
from collections import OrderedDict

taskmatch = re.compile('^.*task-([A-z0-9]+)_run-(\d+).*.nii.gz$')


def _cli():
    parser = generate_parser()
    args = parser.parse_args()
    if args.all:
        args.get_bids_errors = True
        args.generate_map = True
        args.execute_swap = True

    assert args.get_bids_errors or args.generate_map or args.execute_swap, \
        'INPUT: no mode selected!'

    # run stages
    if args.get_bids_errors:
        bids_input = args.bids_input
        output_json = args.error_json
        subject_list = args.subject

        get_bids_errors(bids_input, output_json, subject_list)

    if args.generate_map:
        bids_input = args.bids_input
        input_json = args.error_json
        output_map = args.file_map

        get_bids_errors_correction_map(input_json, output_map, bids_input)

    if args.execute_swap:
        input_map = args.file_map

        swap_files(input_map)


def generate_parser():

    parser = argparse.ArgumentParser(
        description='can be chained together.  For full pipe: '
                    'run_order_fix.py --get-bids-errors --generate-map '
                    '--execute-swap ... inputs',
        epilog='Example call:   ./run_order_fix.py '
               '/mnt/max/shared/projects/ABCD/example_BIDS error.json map.json '
               '--all --subject [NDARINVXXXXXX|sub-NDARINVXXXXXX]'
    )
    modes = parser.add_argument_group(
        title='modes',
        description='flags to execute each of three stages.')
    modes.add_argument(
        '--get-bids-errors', action='store_true',
        help='records all fmri mismatches in the json file.'
    )
    modes.add_argument(
        '--generate-map', action='store_true',
        help='creates a map between errors and true files to swap in the swap '
             'folder.'
    )
    modes.add_argument(
        '--execute-swap', action='store_true',
        help='uses output map file'
    )
    modes.add_argument(
        '--all', action='store_true',
        help='runs start to finish.'
    )
    parser.add_argument(
        '--subject', nargs='+',
        help='optional subject list to narrow down bids inputs. ONLY USED '
             'DURING GET BIDS ERRORS'
    )
    parser.add_argument(
        'bids_input', default=None,
        help='path to bids input folder to detect errors.  Will also fix if '
             '--fix-bids-errors flag is turned on.'
    )
    parser.add_argument(
        'error_json', default='bids_errors.json',
        help='path to bids error json file (output/input depending on mode). '
             'Generated by the --get-bids-errors flag'
    )
    parser.add_argument(
        'file_map', default='file_map.json',
        help='map of files to be swapped around, in format {before: after}, '
             'generated by the --generate-map flag'
    )
    # parser.add_argument(
    #     '--bids-output',
    #     help='path to bids output folder to fix.  Should not be input if the '
    #          'intent is to fix the bids-input folder.'
    # )
    # parser.add_argument(
    #     '--short-json',
    #     help='optional path to an output file which will have no filenames.'
    # )

    return parser


def get_bids_errors(bids_input, output_json, subject_list=None, detailed=False):

    if subject_list:
        subject_list = ['sub-%s' % x if not x.startswith('sub-') else x for x
                        in subject_list]

    func_folders = get_func_folders(bids_input)

    submatch = re.compile('^.*(sub-[A-z0-9]*).*$')
    structured_output = {}

    for folder in func_folders:
        subject = submatch.match(folder).group(1)
        if subject_list and subject not in subject_list:
            continue
        print(subject)
        contents = os.listdir(folder)
        # sort contents
        tasks = task_splitter(contents)
        # filenames
        new = True
        for name, task_set in tasks.items():
            task_set = sorted(task_set)
            run_nums = [int(taskmatch.match(t).group(2)) for t in task_set]
            files = [os.path.join(folder, t) for t in task_set]
            acq_times = [acquisition_time(f) for f in files]
            order = sorted(range(0, len(acq_times)),
                           key=acq_times.__getitem__)
            order = [1 + n for n in order]
            if run_nums == order:
                if detailed:
                    structured_output[subject][name] = 'correct'
                continue
            if new:
                structured_output[subject] = {}
                new = False
            structured_output[subject][name] = {}
            structured_output[subject][name]['current_order'] = run_nums
            structured_output[subject][name]['actual_order'] = order

    if output_json:
        if os.path.exists(output_json):
            os.remove(output_json)
        with open(output_json, 'w') as fd:
            json.dump(structured_output, fd)


def get_bids_errors_correction_map(input_json,  output_map, bids_input=None):
    with open(input_json) as fd:
        jso = json.load(fd)

    mapping = OrderedDict()

    for subject, tasks in jso.items():
        subject_folder = bids_input + '/{subject}/{session}'.format(
            subject=subject, session='ses-baselineYear1Arm1')
        for name, map_data in tasks.items():
            if map_data == 'correct':
                continue
            else:
                if name != 'rest':
                    print('subject %s on %s has bad task data!' % (subject,
                                                                   name))

                current_order = map_data['current_order']
                actual_order = map_data['actual_order']
                if bids_input:
                    current_names = ['task-%s_run-0%s' % (name, i) for i in
                                     current_order]
                    actual_names = ['task-%s_run-0%s' % (name, i) for i in
                                    actual_order]
                else:
                    current_names = ['task-%s0%s' % (name, i) for i in
                                     current_order]
                    actual_names = ['task-%s0%s' % (name, i) for i in
                                    actual_order]
                for (current, end) in zip(current_names, actual_names):
                    mapping.update(
                        generate_file_map(subject_folder, current, end))

    if os.path.exists(output_map):
        os.remove(output_map)
    with open(output_map, 'w') as fd:
        json.dump(mapping, fd, indent=4)


def swap_files(json_file):

    with open(json_file) as fd:
        file_mapper = json.load(fd)
        file_mapper = OrderedDict(sorted(file_mapper.items()))
    swapped = []
    _, tmp = tempfile.mkstemp()
    for before, after in file_mapper.items():
        if before in swapped:
            continue
        try:
            shutil.move(before, tmp)
        except:
            print('failed to move %s' % before)
            raise
        try:
            shutil.move(after, before)
        except:
            print('failed to move %s' % after)
            shutil.move(tmp, before)
            raise
        shutil.move(tmp, after)
        swapped.append(after)


def generate_file_map(subject_directory, current_task, end_task,
                      tempspace=None):
    file_map = {}
    task_directory = subject_directory

    for pathspec in os.walk(task_directory):
        for filepath in (os.path.join(pathspec[0], f) for f in pathspec[2]):
            end_filepath = filepath.replace(current_task, end_task)
            if filepath != end_filepath:
                file_map[filepath] = end_filepath

    return file_map


def get_func_folders(bids_input):
    full_paths = os.walk(bids_input)
    func_paths = filter(lambda x: os.path.basename(x[0]) == 'func', full_paths)
    func_paths = (i[0] for i in func_paths)
    # func_paths = itertools.islice(func_paths, 10)
    return func_paths


def task_splitter(filenames):
    tasks = filter(lambda x: x, (taskmatch.match(x) for x in filenames))
    task_dict = {}
    for t in tasks:
        name = t.group(1)
        if name in task_dict.keys():
            task_dict[name] += [t.string]
        else:
            task_dict[name] = [t.string]

    return task_dict


def acquisition_time(filename):
    sidecar = filename[:-7] + '.json'
    with open(sidecar) as fd:
        jso = json.load(fd)
        time = datetime.datetime.strptime(jso['AcquisitionTime'],
                                          '%H:%M:%S.%f').time()
    return time


if __name__ == '__main__':
    _cli()
