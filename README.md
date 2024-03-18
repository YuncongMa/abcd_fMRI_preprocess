# abcd_fMRI_preprocess
A customizable pipeline to preprocess fMRI data in ABCD dataset, based on [abcd-dicom2bids](https://github.com/ABCD-STUDY/abcd-dicom2bids/tree/master), [fmriprep](https://github.com/nipreps/fmriprep), and [XCP-D](https://github.com/PennLINC/xcp_d)

## Installation
1. Download this package
```
clone https://github.com/YuncongMa/abcd_fMRI_process.git
```

2. Create Conda environment
```
conda create --name abcd python=3.8
```

3. Activate Conda environment
```
conda activate abcd
```

4. Install additional packages
```
pip install numpy bids nibabel
conda install -c conda-forge dcmtk
```
For Apple Silicon, use the homebrew to install dcmtk
```
brew install dcmtk
```
5. Install singularity
https://github.com/sylabs/singularity/releases

6. Add dcm2bids, fmriprep and xcp_d singularity images (.simg)
Check script /tool/download_simg.sh

## Preprocessing Steps
A main python script is used to generate bash scripts for processing ABCD dataset in a cluster environment
```
python abcd_fmri_preprocess_cluster.py
```

1. raw2bids.sh Raw data to BIDS format
2. fmriprep.sh Run fmriprep on BIDS formatted data
3. xcpd.sh Postprocess fMRI data to remove noises
4. collect.sh collect HTML-based reports from fmriprep and xcpd, as well as final preproceesed data

## Other Tools Included
### abcd-dicom2bids 
https://github.com/ABCD-STUDY/abcd-dicom2bids/tree/master
### fmriprep 
https://github.com/nipreps/fmriprep
### XCP-D 
https://github.com/PennLINC/xcp_d
