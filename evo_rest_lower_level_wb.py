# EVO Lower-level ROI analysis - Nipype/Connectome Workbench version

# Holland Brown

# Updated 2023-10-16
# Created 2023-09-22

# Next:
    # add read_json function to my_imaging_tools module (started)
    # decide whether to use wb_command -cifti-average-roi-correlation or Feat GLM for lower levels
    # add step to produce a spec/scene file for easy visualization
    # see ctx-rh-medialorbitofrontal -> https://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/AnatomicalROI/FreeSurferColorLUT
    # Schaefer/Yeo CorticalParcellation with FreeSurfer -> (jrnlart) https://surfer.nmr.mgh.harvard.edu/fswiki/CorticalParcellation_Yeo2011 ; (github repo) https://github.com/ThomasYeoLab/CBIG/tree/master/stable_projects/brain_parcellation/Schaefer2018_LocalGlobal


"""
Consider this procedure...
https://www.mail-archive.com/hcp-users@humanconnectome.org/msg04539.html

1) Extract mean unsmoothed ROI data to text:
wb_command -cifti-roi-average ${subject}_${run}.dtseries.nii 
roi_data_${sub}_${run}_unsmoothed.txt -vol-roi ${sub}_roi_mask.nii # probably works for surface-based ROIs as well but haven't tested
2) Convert extracted ROI data to cifti:
wb_command -cifti-create-scalar-series roi_data_${sub}_${run}_unsmoothed.txt 
roi_data_${sub}_${run}_unsmoothed.dscalar.nii -transpose -series SECOND 0 1
3) Cross-correlate this new ROI timeseries cifti with the smoothed whole-brain 
cifti data:
wb_command -cifti-cross-correlation ${subject}_${run}_smoothed.dtseries.nii 
roi_data_${sub}_${run}_unsmoothed.dscalar.nii 
correlation_${sub}_${run}.dscalar.nii
4) Repeat for all runs and average:
wb_command -cifti-average correlation_${sub}_average.dscalar.nii -cifti 
correlation_${sub}_run1.dscalar.nii -cifti correlation_${sub}_run2.dscalar.nii 
-cifti correlation_${sub}_run3.dscalar.nii -cifti 
correlation_${sub}_run4.dscalar.nii
5) Fisher z transform results:
wb_command -cifti-math "atanh(x)" z_correlation_${sub}_average.dscalar.nii -var 
x correlation_${sub}_average.dscalar.nii

"""

# ---------------------------------------------------------------------------------------------------------------

# %%
import os
import tqdm
import json
import numpy as np
import nibabel as nib
import nilearn as nil
from my_imaging_tools import fmri_tools
# from nipype import Node, Function
# from nipype.interfaces.workbench.cifti import WBCommand

datadir = f'' # where subject folders are located
roidir = f'' # where Lauren's ROI nifti files are located
#rois = ['L_MFG','L_rACC','L_dACC','R_MFG','R_rACC','R_dACC'] # file names (without nifti extension) of Lauren's ROIs
rois = ['L_rACC']

q = fmri_tools(datadir)
sessions = ['1','2']

# fsf_fn = '/holland/Desktop/evo_lower_level.fsf' # /path/to/FeatFileName.fsf
# feat_outdir = 'lower_level_remean.feat' # name of the output directory


# %% Convert CIFTI to "fake nifti"
# cifti_in = f'' # name of cifti input file
# nifti_out = f'' # name of nifti output file
# cmd = [None]*1
# for sub in tqdm(q.subs):
#     subdir = f'{datadir}/{sub}/func/rest'
#     for session in sessions:
#         cifti_input = f'{subdir}/session_{session}/run_1/{cifti_in}' # path to cifti input file
#         nifti_output = f'{subdir}/session_{session}/run_1/{nifti_out}' # path to nifti output file
#         cmd[0] = f'wb_command -cifti-convert -to-nifti {cifti_input} {nifti_output}'

# %% Separate CIFTI files into surface (GIFTI/greyordinate) and subcortical (NIFTI/volumetric) data
# NOTE: Glasser atlas is already separated into GIFTIs

cmd = [None]*3 # allocate memory for commands
for sub in tqdm(q.subs):
    for roi in rois:
        for session in sessions:
            workingdir = f'{datadir}/{sub}/func/rest/session_{session}/run_1'
            inputL = f'{workingdir}/'
            inputR = f'{workingdir}/'
            outputL = f'{workingdir}/'
            outputR = f'{workingdir}/'
            cmd[0] = f'wb_command -cifti-separate {inputL}.dtseries.nii COLUMN -metric CORTEX_LEFT {outputL}.func.gii'
            cmd[1] = f'wb_command -cifti-separate {inputR}.dtseries.nii COLUMN -metric CORTEX_RIGHT {outputR}.func.gii'
            q.exec_cmds(cmd)


# %% Create ROI mask from atlas
from nilearn import datasets

datasets.fetch_atlas_harvard_oxford

      
        
# %% (1) Extract ROI timeseries from ciftis, convert to text files, convert to CIFTIS

cmd_list = [None]*3 # allocate memory for commands
for sub in tqdm(q.subs):
    for roi in rois:
        for session in sessions:
            # nifti_input = f'{datadir}/{sub}/{sub}_{preproc_folder}/{sub}_{nifti_fn}' # subject's preprocessed AFNI ICA results dir
            nifti_input = f''
            new_roi_path = f'' # subject's roi analysis dir
            tsAlready = os.path.exists(f'{new_roi_path}') # check if time series file already exists for this participant
            if tsAlready == False: # if time series file doesn't exist...
                print(f'Extracting ROI time series for {sub}...\n')

                # NEED ROI MASK NIFTI INPUT; also identify input cifti
                roi_label = f'{datadir}/{sub}/anat/T1w/{sub}/label/{label_gifti}'
                cmd_list[0] = 'wb_command -gifti-label-to-roi' # identify an ROI from anatomical parc labels and extract roi cifti
                # cmd_list[1] = f'wb_command -cifti-create-dense-from-template -label {roi_label}' # use label files generated by MEP
                cmd_list[1] = f'wb_command -cifti-roi-average {sub}_{roi}_S{session}.dtseries.nii {sub}_{roi}_S{session}.txt -vol-roi {sub}_roi_mask.nii.gz'
                cmd_list[2] = f'wb_command -cifti-create-scalar-series roi_data_${sub}_${run}_unsmoothed.txt roi_data_${sub}_${run}_unsmoothed.dscalar.nii -transpose -series SECOND 0 1'
                q.exec_cmds(cmd_list) # execute bash commands in system terminal
            else:
                print(f'{roi} time series file already exists for subject {sub}...\n')


# %% (2) Cross-correlate this new ROI timeseries cifti with the smoothed whole-brain cifti data
# wb_command -cifti-cross-correlation ${subject}_${run}_smoothed.dtseries.nii 
# roi_data_${sub}_${run}_unsmoothed.dscalar.nii 
# correlation_${sub}_${run}.dscalar.nii

# %% (3) Fisher z-score the data

# wb_command -cifti-math "atanh(x)" z_correlation_${sub}_average.dscalar.nii -var 
# x correlation_${sub}_average.dscalar.nii

# %% Run Feat GLM on "fake niftis"

# cmd_step1 = [None]*5
# if os.path.exists(f'{datadir}/{fsf_fn}')==False:
#     cmd_step1[0] = f'cp {feat_df} {datadir}' # copy design file into preproc dir
#     print(f'Creating generalized Feat design file for all analyses...\n')

#     # Linux search-and-replace commands
#     cmd_step1[1] = f"sed -i 's/ROI/{roi}/g' {datadir}/{fsf_fn}" # search-and-replace roi in design file
#     cmd_step1[2] = f"sed -i 's/TIMESTEP/{timestep}/g' {datadir}/{fsf_fn}" # search-and-replace subject in design file
#     cmd_step1[3] = f"sed -i 's/INPUTNIFTI/{nifti_fn}/g' {datadir}/{fsf_fn}" # search-and-replace nifti input file name (still have to put correct path into design file before running)
#     cmd_step1[4] = f"sed -i 's/REGIONOFINTERESTTXT/{roi_tn}/g' {datadir}/{fsf_fn}" # search-and-replace ROI text file name (still have to put correct path into design file before running)

# elif os.path.exists(f'{datadir}/{fsf_fn}')==True:
#     cmd_step1[0] = ''
#     print("Generalized Feat design file already exists in main data directory.")



# # duplicate_featdirs = [] # create list to save subject IDs that already had Feat dirs of this name
# for sub in tqdm(q.subs): # Step 2 commands search and replace terms that are different for each participant
#     full_feat_outdir = f'{datadir}/{sub}/{roi}'
#     # if os.path.exists(full_feat_outdir):
#         # print(f'WARNING: Feat directory already exists for {sub}...\nDuplicate Feat dir will be created...\n')
#         # duplicate_featdirs.append(f'{sub}')

#     print(f'Creating Feat design file for subject {sub}...\n')
#     cmd_step2 = [None]*4
#     outdir = f'{datadir}/{sub}/{roi}'
#     cmd_step2[0] = f'cp {datadir}/{fsf_fn} {outdir}' # copy design file into preproc dir

#     # get TR from JSON
#     with open(f'{datadir}/{sub}/func/unprocessed/session_1/run_1/Rest_S1_E1_R1.json', 'rt') as rest_json:
#         rest_info = json.load(rest_json)
#     reptime = rest_info['RepetitionTime']

#     # Linux search-and-replace commands
#     cmd_step2[1] = f"sed -i 's/SUBJ/{sub}/g' {outdir}/{fsf_fn}" # search-and-replace subject in design file
#     cmd_step2[2] = f"sed -i 's/REPTIME/{reptime}/g' {outdir}/{fsf_fn}" # search-and-replace TR in design file
#     cmd_step2[3] = f'feat {outdir}/{fsf_fn}' # run Feat with fsf file
#     q.exec_cmds(cmd_step2) # execute bash commands in system terminal
#     print(f'Running Feat analysis for {sub}...\n')
# print('Feat analyses done.\n\n')



# %% ROI-to-wholebrain correlation
# https://www.humanconnectome.org/software/workbench-command/-cifti-average-roi-correlation

"""

wb_command -cifti-average-roi-correlation

    Averages rows for each map of the ROI(s), takes the correlation of each
    ROI average to the rest of the rows in the same file, applies the fisher
    small z transform, then averages the results across all files.  ROIs are
    always treated as weighting functions, including negative values.  For
    efficiency, ensure that everything that is not intended to be used is
    zero in the ROI map.  If -cifti-roi is specified, -left-roi, -right-roi,
    -cerebellum-roi, and -vol-roi must not be specified.  If multiple
    non-cifti ROI files are specified, they must have the same number of
    columns.

"""

# cmd = [None]*2
# for sub in tqdm(q.subs):
#     for roi_name in rois:
#         roi = f'{roidir}/{roi_name}.nii.gz' # full path to roi nifti file

#         # get TR from JSON
#         with open(f'{datadir}/{sub}/func/unprocessed/session_1/run_1/Rest_S1_E1_R1.json', 'rt') as rest_json:
#             rest_info = json.load(rest_json)
#         TR = rest_info['RepetitionTime']

#         for s in sessions:
#             subdir = f'{datadir}/{sub}/func/rest/session_{s}/run_1'
#             cifti_out = f''
#             cmd[0] = f'wb_command -cifti-average-roi-correlation {cifti_out} - output - output cifti file'
  
