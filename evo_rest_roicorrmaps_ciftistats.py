# EVO Higher-Level ROI Analysis
# Create average correlation maps for each Tx condition and calculate pre- vs. post-Tx difference maps 

# Holland Brown

# Updated 2023-11-30
# Created 2023-11-28

# ---------------------------------------------------------------------------------------------------------------

# %%
import os
# import json
import glob
from my_imaging_tools import fmri_tools

sites = ['NKI','UW']
datadir = f'/athena/victorialab/scratch/hob4003/study_EVO' # where subject folders are located
scriptdir = f'/athena/victorialab/scratch/hob4003/study_EVO/EVO_rs_lower_levels' # where this script, atlas, and my_imaging_tools script are located
wb_command = f'/software/apps/Connectome_Workbench_test/workbench/exe_rh_linux64/wb_command' # /path/to/wb_command package

# datadir = f'/media/holland/EVO_Estia/EVO_MRI/organized/NKI' # where subject folders are located
# scriptdir = f'/media/holland/EVO_Estia/EVO_lowerlev_avg_corrmaps' # where this script, atlas, and my_imaging_tools script are located
# wb_command = f'wb_command' # /path/to/wb_command package, or just 'wb_command'

# q = fmri_tools(datadir)
sessions = ['1','2']
rois=['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']

# %% Calculate resting-state stats for all individual subjects
stats_opts = ['STDEV','VARIANCE','SAMPSTDEV','TSNR','COV','L2NORM','MAX','MIN'] # see wb_command -cifti-stats docs for opts

cmd = [None]*3
command = [None]
for site in sites:
    datadir = f'/athena/victorialab/scratch/hob4003/study_EVO/{site}_MRI_data'
    q = fmri_tools(datadir)
    for sub in q.subs:
        for session in sessions:
            for roi in rois:
                subdir = f'{datadir}/{sub}/func/rois/{roi}'
                cifti_in = f'{subdir}/{sub}_{roi}_S{session}_R1_denoised_aggr_s1.7_wholebrain_crosscorrmap.dscalar.nii'
                output = f'{subdir}/{sub}_{roi}_S{session}_R1_denoised_aggr_s1.7_stats.txt'
                if os.path.isfile(cifti_in):

                    # remove old copy
                    if os.path.isfile(output):
                        command[0] = f'rm {output}'
                        q.exec_cmds(command)

                    # run cmds for each stat
                    for stats_opt in stats_opts:
                        cmd[0] = f'echo \"{stats_opt}\" >> {output}'
                        cmd[1] = f'{wb_command} -cifti-stats {cifti_in} -reduce {stats_opt} >> {output}'
                        cmd[2] = f'echo \"\n\" >> {output}'
                        q.exec_cmds(cmd)
# %%
