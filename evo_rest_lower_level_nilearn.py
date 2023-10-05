# EVO Lower-level ROI analysis - Nipype/Connectome Workbench version

# Holland Brown

# Updated 2023-10-05
# Created 2023-09-22

# Next:
    # add read_json function to my_imaging_tools module (started)
    # decide whether to use wb_command -cifti-average-roi-correlation or Feat GLM for lower levels
    # add step to produce a spec/scene file for easy visualization
    # see ctx-rh-medialorbitofrontal -> https://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/AnatomicalROI/FreeSurferColorLUT


# ---------------------------------------------------------------------------------------------------------------

# %%
import os
import tqdm
import json
import numpy
from my_imaging_tools import fmri_tools
from nilearn.maskers import NiftiMasker
import matplotlib.pyplot as plt
# from nipype import Node, Function
# from nipype.interfaces.workbench.cifti import WBCommand

datadir = f'' # where subject folders are located
roidir = f'' # where Lauren's ROI nifti files are located
#rois = ['L_MFG','L_rACC','L_dACC','R_MFG','R_rACC','R_dACC'] # file names (without nifti extension) of Lauren's ROIs
rois = ['L_rACC']

q = fmri_tools(datadir)
sessions = ['1','2']

# %%
