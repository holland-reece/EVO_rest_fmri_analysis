# EVO Lower-level ROI analysis - Nipype/Connectome Workbench version

# Holland Brown

# Updated 2023-10-06
# Created 2023-09-22

# Next:
    # add read_json function to my_imaging_tools module (started)
    # use Nipype to execute Connectome Workbench commands (for now, use exec_cmds)

#---------------------------------------------------------------------------------------------------------------

# %%
import os
import tqdm
import json
from my_imaging_tools import fmri_tools
# from nipype import Node, Function
# from nipype.interfaces.workbench.cifti import WBCommand

datadir = f'' # where subject folders are located
roidir = f'' # where Lauren's ROI nifti files are located
rois = ['L_MFG'] # file names (without nifti extension) of Lauren's ROIs

q = fmri_tools(datadir)
sessions = ['1','2']

fsf_fn = '/holland/Desktop/evo_lower_level.fsf' # /path/to/FeatFileName.fsf
# feat_outdir = 'lower_level_remean.feat' # name of the output directory


# %% Convert CIFTI to "fake nifti"
cifti_in = f'' # name of cifti input file
nifti_out = f'' # name of nifti output file
cmd = [None]*1
for sub in tqdm(q.subs):
    subdir = f'{datadir}/{sub}/func/rest'
    for session in sessions:
        cifti_input = f'{subdir}/session_{session}/run_1/{cifti_in}' # path to cifti input file
        nifti_output = f'{subdir}/session_{session}/run_1/{nifti_out}' # path to nifti output file
        cmd[0] = f'wb_command -cifti-convert -to-nifti {cifti_input} {nifti_output}'





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
        
        
# %% Extract ROI timeseries from "fake niftis" for input into Level 1 analysis
# fslmeants -> output avg time series of set of voxels, or indiv time series for each of specified voxels

cmd_list = [None]*1 # reserve memory for commands
for sub in tqdm(q.subs):
    for roi in rois:
        # nifti_input = f'{datadir}/{sub}/{sub}_{preproc_folder}/{sub}_{nifti_fn}' # subject's preprocessed AFNI ICA results dir
        nifti_input = f''
        new_roi_path = f'' # subject's roi analysis dir
        tsAlready = os.path.exists(f'{new_roi_path}') # check if time series file already exists for this participant
        if tsAlready == False: # if time series file doesn't exist...
            print(f'Extracting ROI time series for {sub}...\n')
            cmd_list[0] = f'fslmeants -i {nifti_input} -o {new_roi_path} -m {roidir}/{roi}/{roi}.nii.gz' # calculate mean time series; function takes (1) path to input NIfTI, (2) path to output text file, (3) path to mask NIfTI
            q.exec_cmds(cmd_list) # execute bash commands in system terminal
        else:
            print(f'{roi} time series file already exists for subject {sub}...\n')


# %% Run Feat GLM on "fake niftis"

cmd_step1 = [None]*5
if os.path.exists(f'{datadir}/{fsf_fn}')==False:
    cmd_step1[0] = f'cp {feat_df} {datadir}' # copy design file into preproc dir
    print(f'Creating generalized Feat design file for all analyses...\n')

    # Linux search-and-replace commands
    cmd_step1[1] = f"sed -i 's/ROI/{roi}/g' {datadir}/{fsf_fn}" # search-and-replace roi in design file
    cmd_step1[2] = f"sed -i 's/TIMESTEP/{timestep}/g' {datadir}/{fsf_fn}" # search-and-replace subject in design file
    cmd_step1[3] = f"sed -i 's/INPUTNIFTI/{nifti_fn}/g' {datadir}/{fsf_fn}" # search-and-replace nifti input file name (still have to put correct path into design file before running)
    cmd_step1[4] = f"sed -i 's/REGIONOFINTERESTTXT/{roi_tn}/g' {datadir}/{fsf_fn}" # search-and-replace ROI text file name (still have to put correct path into design file before running)

elif os.path.exists(f'{datadir}/{fsf_fn}')==True:
    cmd_step1[0] = ''
    print("Generalized Feat design file already exists in main data directory.")



# duplicate_featdirs = [] # create list to save subject IDs that already had Feat dirs of this name
for sub in tqdm(q.subs): # Step 2 commands search and replace terms that are different for each participant
    full_feat_outdir = f'{datadir}/{sub}/{roi}'
    # if os.path.exists(full_feat_outdir):
        # print(f'WARNING: Feat directory already exists for {sub}...\nDuplicate Feat dir will be created...\n')
        # duplicate_featdirs.append(f'{sub}')

    print(f'Creating Feat design file for subject {sub}...\n')
    cmd_step2 = [None]*4
    outdir = f'{datadir}/{sub}/{roi}'
    cmd_step2[0] = f'cp {datadir}/{fsf_fn} {outdir}' # copy design file into preproc dir

    # get TR from JSON
    with open(f'{datadir}/{sub}/func/unprocessed/session_1/run_1/Rest_S1_E1_R1.json', 'rt') as rest_json:
        rest_info = json.load(rest_json)
    reptime = rest_info['RepetitionTime']

    # Linux search-and-replace commands
    cmd_step2[1] = f"sed -i 's/SUBJ/{sub}/g' {outdir}/{fsf_fn}" # search-and-replace subject in design file
    cmd_step2[2] = f"sed -i 's/REPTIME/{reptime}/g' {outdir}/{fsf_fn}" # search-and-replace TR in design file
    cmd_step2[3] = f'feat {outdir}/{fsf_fn}' # run Feat with fsf file
    q.exec_cmds(cmd_step2) # execute bash commands in system terminal
    print(f'Running Feat analysis for {sub}...\n')
print('Feat analyses done.\n\n')



# %% Convert "fake niftis" back to ciftis
