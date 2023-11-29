# EVO Post-Multiecho-Preproc-Pipeline Lower-Level Mixed Effects Linear Model Using Feat

# Holland Brown

# Updated 2023-11-29
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
# datadir = f'/athena/victorialab/scratch/hob4003/study_EVO' # where subject folders are located
# scriptdir = f'/athena/victorialab/scratch/hob4003/study_EVO/EVO_rs_lower_levels' # where this script, atlas, and my_imaging_tools script are located
# wb_command = f'/software/apps/Connectome_Workbench_test/workbench/exe_rh_linux64/wb_command' # /path/to/wb_command package

home_dir = f'/home/holland/Desktop/EVO_TEST' # where subject folders are located
datadir = f'{home_dir}/subjects' # where this script, atlas, and my_imaging_tools script are located
wb_command = f'wb_command' # /path/to/wb_command package, or just 'wb_command'

q = fmri_tools(datadir)
sessions = ['1','2']
rois=['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']
input_nifti = 'denoised_func_data_aggr' # without extension; ac/pc aligned, denoised with ICA-AROMA

# %% Use FreeSurfer script to create volumetric ROI mask from Glasser MMP atlas for each subject
subject_list = f'subjectslist.txt'
annot_file = f'HCP-MMP1'
output_dir = f'{home_dir}/'

cmd = [None]
for sub in q.subs:
    cmd = f'create_subj_volume_parcellation -L <subject_list> -a <name_of_annot_file> -d <name_of_output_dir>'

# %% Run linear model for each subject, each ROI, and each session, comparing wholebrain to ROI activation
# %% 6. Run lower-level analysis using design template (ref: first_level5.sh)
feat_fn = f''
feat_df = f''

for sub in q.subs:
    for session in sessions:

        # get TR (i.e. timestep) from JSON
        json = f'{datadir}/{sub}/func/unprocessed/session_{session}/run_1/Rest_S{session}_R1_E1.json'
        with open(f'{datadir}/{sub}/func/unprocessed/rest/session_{session}/run_1/Rest_S{session}_R1_E1.json', 'rt') as func_json:
            func_info = json.load(func_json)
        timestep = func_info['RepetitionTime']
        print(timestep)

        for roi in rois:
            # Step 1 commands search and replace terms in design file that are the same for all subjects
            cmd_step1 = [None]*5
            if os.path.exists(f'{datadir}/{feat_fn}')==False:
                cmd_step1[0] = f'cp {feat_df} {datadir}' # copy design file into preproc dir
                print(f'Creating generalized Feat design file for all analyses...\n')

                # Linux search-and-replace commands
                cmd_step1[1] = f"sed -i 's/ROI/{roi}/g' {datadir}/{feat_fn}" # search-and-replace roi in design file
                cmd_step1[2] = f"sed -i 's/TIMESTEP/{timestep}/g' {datadir}/{feat_fn}" # search-and-replace TR in design file
                cmd_step1[3] = f"sed -i 's/INPUTNIFTI/{nifti_fn}/g' {datadir}/{feat_fn}" # search-and-replace nifti input file name (still have to put correct path into design file before running)
                cmd_step1[4] = f"sed -i 's/REGIONOFINTERESTTXT/{roi_tn}/g' {datadir}/{feat_fn}" # search-and-replace ROI text file name (still have to put correct path into design file before running)

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


# %% Run linear model for each subject
