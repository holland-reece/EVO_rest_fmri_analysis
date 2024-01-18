# EVO Lower-level ROI analysis

# Holland Brown

# Updated 2023-06-16
# Created 2023-03-20

# Recent changes:
    # 2023-05-18: expanded read subject list section to automatically adjust for only running 1 site's ppts and change TR accordingly
    # 2023-04-21: added statement in remean block to delete previous gsr nifti file if both remean & gsr are run (final nifti input is both gsr & remean)
    # 2023-04-18: removed try/except statements (may have been interfering w/ handoff between code body and functions, or silencing error messages)

# NOTE: FEAT output functional file is in subject's functional (not structural) space

#---------------------------------------------------------------------------------------------------------------
# %% Setup 1: Define functions and import modules

import subprocess
import os
import tqdm
import json
from my_imaging_tools import fmri_tools




# Setup 2: User run options
rois = ['L_MFG'] # name of ROI mask, will be used to create directories and Feat design file
operating_system = 0 # 0 for Linux, 1 for Mac OS
run_create_roi_dirs = 0 # run Step 4 -> makes an ROI directory in each participant's directory; this is where Feat ana dir, fsf file and txt file will go
run_remean = 1 # run Step 2 (only if necessary) -> see notes on WMECC and EVO studies
run_extract_timeseries = 1 # run Step 3 -> takes nifti data file and nifti mask file, returns roi text file for lower level Feat input
run_lower_level_ana = 1 # run Step 5 -> lower level Feat analysis


# Setup 3: File names and directories
feat_fn = 'evo_lower_level.fsf' # FeatFileName.fsf
sublist_tf = f'rest_preproc_NKI.txt' # SubjectListName.txt
preproc_folder = 'rest_preproc.feat' # PreprocessedInputsFolder -> omit subject ID from beginning, will look like dir/<subjectID>_PreprocessedInputsFolder
nifti_fn = 'filtered_func_aggrdenois_bptf_std.nii.gz' # NiftiInputFileName.nii.gz -> fn after AFNI-NIFTI conversion, will be <subjectID>_NiftiInputFileName.nii.gz
nifti_remean_fn = 'filt_func_aggrdenois_bptf_std_remean.nii.gz'
# roi_tn = '_aggr_remean.txt' # leave out roi name and underscore -> will be concatenated w roi name, so you can just make it '.txt'


datadir = '/media/holland/LACIE-SHARE/EVO_MRI_data' # main data directory
roi_dir = '/media/holland/LACIE-SHARE/EVO_ROIs' # directory where ROI masks are located
feat_df = f'{datadir}/{feat_fn}' # full/path/to/{feat_fn}
sublist = f'/home/holland/Desktop/{sublist_tf}'

q = fmri_tools(datadir)
sessions = ['1','2']



# %% Create ROI dirs in every ppt's dir (ref: MkDir_ROI)
if run_create_roi_dirs == 1:
    numdirsCreated = 0 # counter -> number of directories created
    cmd_list = [''] # define bash commands
    for sub in q.subs:
        new_dir = f'{datadir}/{sub}/{roi}'
        dir_exists = os.path.exists(new_dir)
        if dir_exists == False:
            numdirsCreated += 1
            cmd_list[0] = f'mkdir {datadir}/{sub}/{roi}' # create ROI dir in subj dir
            q.exec_cmds(cmd_list) # execute bash commands in system terminal
        else:
            print(f'ROI directory already exists for {sub}.\n')
    print(f'{numdirsCreated} ROI directories created.\n\n')

# Re-mean (do this if activation maps are total null; fsl expects data to be centered at 10,000)
# adds 10,000 to EPI file before time series extraction to shift mean (time-series extraction takes mean activation of roi)
if run_remean == 1:
    for sub in q.subs:
        preproc_dir = f'{datadir}/{sub}/{preproc_folder}'
        # preproc_dir = f'{datadir}/{sub}'
        remeanExists = os.path.exists(f'{preproc_dir}/{nifti_remean_fn}')
        if remeanExists == False:
            print(f'Translating global mean by 10,000 for {sub}...\n')
            cmd_remean = f'fslmaths {preproc_dir}/{nifti_fn} -add 10000 {preproc_dir}/{nifti_remean_fn}'
            q.exec_cmds([cmd_remean])
        else:
            print(f'Remeaned NIfTI file already exists for subject {sub}...\n')
    print('EPI files remeaned.')
    nifti_fn = nifti_remean_fn # rename main nifti input file to be the remeaned nifti file
    print(f'NIfTI input file is now "{nifti_fn}".\n\n')
    

# %% Extract timeseries from ROIs for input into Level 1 analysis (ref: ROI_timeseries.sh)
# fslmeants -> output avg time series of set of voxels, or indiv time series for each of specified voxels
if run_extract_timeseries == 1:
    cmd_list = [''] # reserve memory for commands
    cmd=['','']
    for sub in q.subs:
        mask = f'{datadir}/{sub}/{preproc_folder}/{roi}.nii.gz'

        # Extract ROI timeseries
        nifti_input = f'{datadir}/{sub}/{preproc_folder}/{nifti_fn}'
        new_roi_path = f'{datadir}/{sub}/{roi}/{roi}_timepoints.txt' # subject's roi analysis dir
        tsAlready = os.path.exists(f'{new_roi_path}') # check if time series file already exists for this participant
        if tsAlready == False: # if time series file doesn't exist...
            print(f'Extracting ROI time series for {sub}...\n')
            cmd_list[0] = f'fslmeants -i {nifti_input} -o {new_roi_path} -m {mask}' # calculate mean time series; function takes (1) path to input NIfTI, (2) path to output text file, (3) path to mask NIfTI
            q.exec_cmds(cmd_list) # execute bash commands in system terminal
        else:
            print(f'ROI time series file already exists for subject {sub}...\n')

# %% 6. Run lower-level analysis using design template (ref: first_level5.sh)
if run_lower_level_ana == 1: # Step 1 commands search and replace terms in design file that are the same for all subjects
    cmd_step1 = ['','','','','']
    if os.path.exists(f'{datadir}/{feat_fn}')==False:
        cmd_step1[0] = f'cp {feat_df} {datadir}' # copy design file into preproc dir
        print(f'Creating generalized Feat design file for all analyses...\n')

        # Linux search-and-replace commands
        if operating_system == 0:
            cmd_step1[1] = f"sed -i 's/ROI/{roi}/g' {datadir}/{feat_fn}" # search-and-replace roi in design file
            cmd_step1[2] = f"sed -i 's/TIMESTEP/{timestep}/g' {datadir}/{feat_fn}" # search-and-replace subject in design file
            cmd_step1[3] = f"sed -i 's/INPUTNIFTI/{nifti_fn}/g' {datadir}/{feat_fn}" # search-and-replace nifti input file name (still have to put correct path into design file before running)
            cmd_step1[4] = f"sed -i 's/REGIONOFINTERESTTXT/{roi_tn}/g' {datadir}/{feat_fn}" # search-and-replace ROI text file name (still have to put correct path into design file before running)

        # MacOS search-and-replace commands
        elif operating_system == 1:
            cmd_step1[1] = f"sed -i '' s/ROI/{roi}/g {datadir}/{feat_fn}" # search-and-replace roi in design file
            cmd_step1[2] = f"sed -i '' s/TIMESTEP/{timestep}/g {datadir}/{feat_fn}" # search-and-replace subject in design file
            cmd_step1[3] = f"sed -i '' s/INPUTNIFTI/{nifti_fn}/g {datadir}/{feat_fn}" # search-and-replace nifti input filename (still have to put correct path into design file before running)
            cmd_step1[4] = f"sed -i '' s/REGIONOFINTERESTTXT/{roi_tn}/g {datadir}/{feat_fn}" # search-and-replace ROI text file name (still have to put correct path into design file before running)
        exec_cmds(cmd_step1) # execute bash commands in system terminal
        print("Done.")

    elif os.path.exists(f'{datadir}/{feat_fn}')==True:
        cmd_step1[0] = ''
        print("Generalized Feat design file already exists in main data directory.")
    

    for sub in subs: # Step 2 commands search and replace terms that are different for each participant
        print(f'Creating Feat design file for subject {sub}...\n')
        cmd_step2 = ['','','']
        outdir = f'{datadir}/{sub}/{roi}'
        cmd_step2[0] = f'cp {datadir}/{feat_fn} {outdir}' # copy design file into preproc dir

        if operating_system == 0: # Linux search-and-replace commands
            cmd_step2[1] = f"sed -i 's/SUBJ/{sub}/g' {outdir}/{feat_fn}" # search-and-replace subject in design file
        elif operating_system == 1: # MacOS search-and-replace commands
            cmd_step2[1] = f"sed -i '' s/SUBJ/{sub}/g {outdir}/{feat_fn}" # search-and-replace roi in design file
        cmd_step2[2] = f'feat {outdir}/{feat_fn}' # run fsf file
        exec_cmds(cmd_step2) # execute bash commands in system terminal
        print(f'Running Feat analysis for {sub}...\n')
    print('Feat analyses done.\n\n')

for sub in q.subs:
    outdir = f'{datadir}/{sub}/{roi}'
    cmd=f'feat {outdir}/{feat_fn}'
    print(f'Running Feat analysis for {sub}...\n')
    q.exec_cmds([cmd])
print('Feat analyses done.\n\n')
# %%
