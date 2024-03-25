#! /usr/bin/env python3
# Yuncong Ma, 3/25/2024
# Perform quality control on BIDS formatted MRI data

import os, sys, argparse, re, subprocess
from bids import BIDSLayout
import numpy as np

from Data_Input import *
from Visualization import *


def generate_parser(parser=None):
    """
    Generates the command line parser for this program.
    :param parser: optional subparser for wrapping this program as a submodule.
    :return: ArgumentParser for this script/module
    """
    if not parser:
        parser = argparse.ArgumentParser(
            description='qc_bids is to perform quality control on BIDS formatted MRI data'
        )
    parser.add_argument(
        '--bids', dest='dir_bids',
        help='path to the input bids dataset root directory.'
    )
    parser.add_argument(
        '--sub', dest='subject',
        help='subject info'
    )
    parser.add_argument(
        '--ses', dest='session',
        help='session info'
    )
    parser.add_argument(
        '-o', dest='dir_qc_bids',
        help="output directory"
    )

    return parser


def qc_bids_image_sample(file_image: str, file_figure: str, figure_title: str, brain_map=None):
    """
    Give a simple 3 orthogonal view image sample at the image center
    :param file_image:
    :param file_figure:
    :param brain_map: None or image data
    :return:
    """

    if brain_map is None:
        brain_map = load_fmri_scan(file_image, 'Volume', 'Volume (*.nii, *.nii.gz, *.mat)', Concatenation=False)

    image_size = brain_map.shape
    if len(image_size) > 3:
        brain_map = brain_map[:, :, :, 0]
        image_size = image_size[:3]

    brain_template = {'Brain_Mask': np.ones(image_size), 'Overlay_Image': brain_map}

    brain_map /= np.max(brain_map)

    color_function = color_theme('Seed_Map_3_Positive', [2, 3])
    # view_center = np.array(np.round(np.array(image_size[:3])/2), dtype=int)
    view_center = 'max_value'

    plot_FN_brain_volume_3view(brain_map, brain_template,
                               color_function=color_function, threshold=2,
                               view_center=view_center,
                               file_output=file_figure,
                               figure_title=figure_title)

    return()


def main(argv=sys.argv):
    parser = generate_parser()
    args = parser.parse_args()

    print('Start qc_bids')

    # directory to the toolbox
    dir_qc = os.path.dirname(os.path.abspath(__file__))
    # report template
    file_template_qc_bids = os.path.join(dir_qc, 'web_template_qc_bids.html')
    with open(file_template_qc_bids, 'r') as file:
        template_content = file.read()

    # output directory
    dir_qc_sub = os.path.join(args.dir_qc_bids, "sub-"+args.subject, "ses-"+args.session)
    dir_qc_sub_figure = os.path.join(dir_qc_sub, 'bids_qc_figure')
    if not os.path.exists(dir_qc_sub_figure):
        os.makedirs(dir_qc_sub)
        os.makedirs(dir_qc_sub_figure)

    # copy results from BIDS to BIDS_QC
    # dir_bids_sub = os.path.join(args.dir_bids, "sub-"+args.subject, "ses-"+args.session)
    # subprocess.run(['cp', '-r', dir_bids_sub+'/', dir_qc_sub])

    # basic info
    template_content = template_content.replace('{$subject$}', args.subject) \
                                       .replace('{$session$}', args.session) \
                                       .replace('{$report_time$}', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

    # Load the bids layout
    layout = BIDSLayout(args.dir_bids, is_derivative=True)

    list_datatype = ['anat', 'fmap', 'func']
    n_datatype = len(list_datatype)
    content = {'anat': '', 'fmap': '<text style="font-size:20px;">\n', 'func': '<text style="font-size:20px;">\n'}
    count_content = np.zeros(n_datatype, dtype=int)

    for i in range(n_datatype):
        list_image = layout.get(subject=args.subject, session=args.session, datatype=list_datatype[i], extension='.nii.gz')

        # get basic MRI info and make figures
        for file_image in [os.path.join(x.dirname, x.filename) for x in list_image]:
            MRI_image = load_fmri_scan(file_image, 'Volume', 'Volume (*.nii, *.nii.gz, *.mat)', Concatenation=False)
            count_content[i] += 1
            content[list_datatype[i]] += '<text style="font-size:20px;">\n' + str(count_content[i]) + '. '
            content[list_datatype[i]] += 'File name: ' + os.path.basename(file_image)
            content[list_datatype[i]] += '   image size: ' + str(MRI_image.shape) + '<br/>\n'
            content[list_datatype[i]] += '\n</text>'
            # plot
            subject_session = "sub-"+args.subject + "_ses-"+args.session + "_"
            file_name = os.path.basename(file_image).replace('.nii.gz', '')
            figure_title = list_datatype[i] + '\n  \n' + file_name[len(subject_session):]
            qc_bids_image_sample(file_image, os.path.join(dir_qc_sub_figure, os.path.basename(file_image).replace('.nii.gz', '.jpg')),
                                 figure_title=figure_title, brain_map=MRI_image)

        if list_datatype[i] == 'anat':
            list_image = layout.get(subject=args.subject, session=args.session, datatype=list_datatype[i], suffix='T1w', extension='.nii.gz')
            content[list_datatype[i]] += '\n<p align="center">'
            for file_image in [os.path.join(x.dirname, x.filename) for x in list_image]:
                content[list_datatype[i]] += '\n  <img class="toggleImage greenBorder", src="'+os.path.join('bids_qc_figure', os.path.basename(file_image).replace('.nii.gz', '.jpg'))+'", width="200px">'
            content[list_datatype[i]] += '\n  <img src="", style="padding-right: 50px;">'
            list_image = layout.get(subject=args.subject, session=args.session, datatype=list_datatype[i], suffix='T2w', extension='.nii.gz')
            for file_image in [os.path.join(x.dirname, x.filename) for x in list_image]:
                content[list_datatype[i]] += '\n  <img class="toggleImage greenBorder", src="'+os.path.join('bids_qc_figure', os.path.basename(file_image).replace('.nii.gz', '.jpg'))+'", width="200px">'
            content[list_datatype[i]] += '\n</p>\n'

        if list_datatype[i] == 'fmap':
            flag_fmap_AP = ""
            list_image = layout.get(subject=args.subject, session=args.session, datatype=list_datatype[i], direction='AP', extension='.nii.gz')
            content[list_datatype[i]] += '\n<p align="center">'
            for file_image in [os.path.join(x.dirname, x.filename) for x in list_image]:
                content[list_datatype[i]] += '\n  <img class="toggleImage greenBorder", src="'+os.path.join('bids_qc_figure', os.path.basename(file_image).replace('.nii.gz', '.jpg'))+'", width="200px">'
                json_path = file_image.replace('.nii.gz', '.json')
                with open(json_path, 'r') as f:
                    data = json.load(f)
                if len(data["IntendedFor"]) > 0:
                    flag_fmap_AP = os.path.basename(file_image)
            content[list_datatype[i]] += '\n</p>\n'
            flag_fmap_PA = ""
            list_image = layout.get(subject=args.subject, session=args.session, datatype=list_datatype[i], direction='PA', extension='.nii.gz')
            content[list_datatype[i]] += '\n<p align="center">'
            for file_image in [os.path.join(x.dirname, x.filename) for x in list_image]:
                content[list_datatype[i]] += '\n  <img class="toggleImage greenBorder", src="'+os.path.join('bids_qc_figure', os.path.basename(file_image).replace('.nii.gz', '.jpg'))+'", width="200px">'
                json_path = file_image.replace('.nii.gz', '.json')
                with open(json_path, 'r') as f:
                    data = json.load(f)
                if len(data["IntendedFor"]) > 0:
                    flag_fmap_PA = os.path.basename(file_image)
            content[list_datatype[i]] += '\n</p>\n'
            content[list_datatype[i]] += '<text style="font-size:20px;">\nField map pair selected in raw2bids: <br />\n'+flag_fmap_AP+' <br />\n'+flag_fmap_PA+' <br />\n</p>\n'

        if list_datatype[i] == 'func':
            list_image = layout.get(subject=args.subject, session=args.session, datatype=list_datatype[i], extension='.nii.gz')
            content[list_datatype[i]] += '\n<p align="center">'
            for file_image in [os.path.join(x.dirname, x.filename) for x in list_image]:
                content[list_datatype[i]] += '\n  <img class="toggleImage greenBorder", src="'+os.path.join('bids_qc_figure', os.path.basename(file_image).replace('.nii.gz', '.jpg'))+'", width="200px">'
            content[list_datatype[i]] += '\n</p>\n'

    for i in range(n_datatype):
        template_content = template_content.replace('{$content_'+list_datatype[i]+'$}', content[list_datatype[i]])

    file_report = open(os.path.join(args.dir_qc_bids, "sub-"+args.subject, "ses-"+args.session, 'bids_qc_report.html'), 'w')
    print(template_content, file=file_report)
    file_report.close()

    print('Finish qc_bids')


if __name__ == "__main__":
    sys.exit(main())
