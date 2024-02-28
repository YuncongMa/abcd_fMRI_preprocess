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
conda install -c conda-forge dcm2bids
conda install -c conda-forge dcm2niix
conda install -c conda-forge dcmtk
```
For Apple Silicon, use the homebrew to install dcmtk
```
brew install dcmtk
```

## Preprocessing Steps
### 1. Raw data to BIDS format
```
python abcd_raw2bids.py
```
### 2. fmriprep

### 3. XCP-D

### 4. Quality control

## Other Tools Included
### abcd-dicom2bids 
https://github.com/ABCD-STUDY/abcd-dicom2bids/tree/master
### fmriprep 
https://github.com/nipreps/fmriprep
### XCP-D 
https://github.com/PennLINC/xcp_d
