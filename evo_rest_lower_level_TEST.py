# %% TEST: ROI-to-wholebrain analysis with HCP MMP1.0 Atlas (Glasser 2016)
# import os
import tqdm
# import json
# import numpy as np
# import nibabel as nib
# import nilearn as nil
from my_imaging_tools import fmri_tools

datadir = f'/home/holland/Desktop/EVO_TEST' # where subject folders are located
atlasdir = f'/home/holland/Desktop/EVO_atlas_search' # where HCP MMP1.0 files are located (downloaded from BALSA)
rois = ['L_MFG'] # names of ROI text files containing HCP MMP1.0 ROI label names
q = fmri_tools(datadir)


# %% Create ROI mask
cmd = [None]*3
for sub in tqdm(q.subs):
    for roi in rois:
        subjectdir = f'{datadir}/{sub}'
        input_cifti = f'{subjectdir}'
        subject_left_surface = f'{subjectdir}'
        subject_right_surface = f'{subjectdir}'
        output_roi = f'{subjectdir}'
        cmd[0] = f'wb_command -cifti-roi -cifti {input_cifti}.dscalar.nii -roi_file {roi}.txt -left_surface {subject_left_surface}.gii -right-surface {subject_right_surface}.gii -output {output_roi}.dscalar.nii'
        q.exec_cmds(cmd)
