# EVO Post-Multiecho-Preproc-Pipeline Lower-Level Mixed Effects Linear Model Using Feat

# Holland Brown

# Updated 2023-12-13
# Created 2023-11-28

# Separate linear model for each subject, 2 repeated measures (sessions), 6 ROIs

# Sources:
    # HCP-MMP1.0 projected onto fsaverage space: https://figshare.com/articles/dataset/HCP-MMP1_0_projected_on_fsaverage/3498446
    # script to create subject-specific parcellated image in fsaverage space: https://figshare.com/articles/dataset/HCP-MMP1_0_volumetric_NIfTI_masks_in_native_structural_space/4249400?file=13320527

# --------------------------------------------------------------------------------------
# %%
import os
# import json
import glob
from my_imaging_tools import fmri_tools

site = 'NKI'
datadir = f'/athena/victorialab/scratch/hob4003/study_EVO' # where subject folders are located
# scriptdir = f'/athena/victorialab/scratch/hob4003/study_EVO/EVO_rs_lower_levels' # where this script, atlas, and my_imaging_tools script are located
# wb_command = f'/software/apps/Connectome_Workbench_test/workbench/exe_rh_linux64/wb_command' # /path/to/wb_command package

# home_dir = f'/home/holland/Desktop/EVO_TEST' # where subject folders are located
# datadir = f'{home_dir}/subjects' # where this script, atlas, and my_imaging_tools script are located
# wb_command = f'wb_command' # /path/to/wb_command package, or just 'wb_command'

q = fmri_tools(datadir)
sessions = ['1','2']
runs = ['1']
rois=['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
input_nifti = 'denoised_func_data_aggr' # without extension; ac/pc aligned, denoised with ICA-AROMA

# %% Create ROI masks for each subject
for sub in q.subs:
    for roi in rois:
        hcp_parcs_dir = f'' # subject's HCP-MMP1 roi masks dir

# %% Extract timeseries from ROIs for input into Level 1 analysis (ref: ROI_timeseries.sh)
# fslmeants -> output avg time series of set of voxels, or indiv time series for each of specified voxels
cmd=[None]
for sub in q.subs:
    for session in sessions:
        for run in runs:
            for roi in rois:
                mask = f'{datadir}/{sub}/func/rest/rois/{roi}_bin.nii.gz' # subjects binarized ROI mask
                func_nifti = f'{datadir}/{sub}/func/rest/session_{session}/run_{run}/Rest_E1_acpc.nii.gz' # subject rest func nifti
                roi_ts = f'{datadir}/{sub}/func/rest/rois/{roi}/{roi}_S{session}_R{run}_timepoints.txt' # output text file containing ROI time series

                if os.path.exists(f'{roi_ts}') == False:
                    # print(f'Extracting ROI time series for {sub}...\n')
                    cmd[0] = f'fslmeants -i {func_nifti} -o {roi_ts} -m {mask}' # calculate mean time series; function takes (1) path to input NIfTI, (2) path to output text file, (3) path to mask NIfTI
                    q.exec_cmds(cmd) # execute bash commands in system terminal
                # else:
                #     print(f'ROI time series file already exists for subject {sub}...\n')

# %% 6. Run lower-level analysis using design template (ref: first_level5.sh)
feat_fn = f''
feat_df = f''
func_fn = 'Rest_E1_acpc.nii.gz'

cmd=[None]
commands = [None]*8
for sub in q.subs:
    for session in sessions:
            for run in runs:
                # func_nifti = f'{datadir}/{sub}/func/rest/session_{session}/run_{run}/Rest_E1_acpc.nii.gz'

                # Get TR (i.e. timestep) from JSON
                json = f'{datadir}/{sub}/func/unprocessed/session_{session}/run_{run}/Rest_S{session}_R1_E1.json'
                with open(f'{datadir}/{sub}/func/unprocessed/rest/session_{session}/run_{run}/Rest_S{session}_R1_E1.json', 'rt') as func_json:
                    func_info = json.load(func_json)
                timestep = func_info['RepetitionTime']
                # print(timestep)
                
                for roi in rois:
                    session_dir = f'{datadir}/{sub}/func/rest/rois/{roi}/session_{session}'
                    outdir = f'{session_dir}/run_{run}'

                    if os.path.isdir(session_dir)==False:
                        cmd[0] = f'mkdir {session_dir}'
                        q.exec_cmds(cmd)

                    if os.path.isdir(outdir)==False:
                        cmd[0] = f'mkdir {outdir}'
                        q.exec_cmds(cmd)

                    # roi_ts = f'{datadir}/{sub}/func/rest/rois/{roi}/{roi}_S{session}_R{run}_timepoints.txt'
                    roi_tn = f'{roi}_S{session}_R{run}_timepoints.txt'

                    # Create design.fsf template for this ROI
                    if os.path.isfile(f'{datadir}/{sub}/func/rest/rois/{roi}/{roi}_S{session}_R{run}_design.fsf')==False:
                        commands[0] = f'cp {feat_df} {outdir}' # copy design file into preproc dir
                        commands[1] = f"sed -i 's/ROI/{roi}/g' {outdir}/{feat_fn}"
                        commands[2] = f"sed -i 's/TIMESTEP/{timestep}/g' {outdir}/{feat_fn}"
                        commands[3] = f"sed -i 's/INPUTNIFTI/{func_fn}/g' {outdir}/{feat_fn}" # (still have to put correct path into design file before running)
                        commands[4] = f"sed -i 's/REGIONOFINTERESTTXT/{roi_tn}/g' {outdir}/{feat_fn}" # (still have to put correct path into design file before running)
                        commands[5] = f"sed -i 's/SUBJ/{sub}/g' {outdir}/{feat_fn}"
                        commands[6] = f"sed -i 's/SESSION/{session}/g' {outdir}/{feat_fn}"
                        commands[7] = f"sed -i 's/MRIRUN/{run}/g' {outdir}/{feat_fn}"
                        q.exec_cmds(commands)

                    cmd[0] = f'feat {outdir}/{feat_fn}' # run fsf file
                    q.exec_cmds(cmd)

                    print(f'\n-------- Running Feat analysis for {sub} --------\n')
print('\n-------- Feat analyses done. --------\n\n')



# %% Run linear model for each subject
