# %% TEST: ROI-to-wholebrain analysis with HCP MMP1.0 Atlas (Glasser 2016)
import os
import tqdm
import json
import numpy as np
import nibabel as nib
import nilearn as nil
from my_imaging_tools import fmri_tools

datadir = f'/home/holland/Desktop' # where subject folders are located
atlasdir = f'/home/holland/Desktop/EVO_atlas_search' # where HCP MMP1.0 files are located (downloaded from BALSA)
rois = ['R_p24_ROI','L_p24_ROI'] # HCP MMP1.0 region codes