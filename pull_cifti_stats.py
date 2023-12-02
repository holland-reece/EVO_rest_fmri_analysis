# EVO Higher-Level ROI Analysis
# Higher-level modeling with cifti stats from text files

# Holland Brown

# Updated 2023-12-01
# Created 2023-12-01

# ---------------------------------------------------------------------------------------------------------------

# %%
import os
from my_imaging_tools import fmri_tools

sites = ['NKI','UW']
maindatadir = f'/athena/victorialab/scratch/hob4003/study_EVO' # where subject folders are located
restdir = f'/athena/victorialab/scratch/hob4003/study_EVO/EVO_rest' # where to create folder of cifti stats txt files
wb_command = f'/software/apps/Connectome_Workbench_test/workbench/exe_rh_linux64/wb_command' # /path/to/wb_command package

# q = fmri_tools(datadir)
sessions = ['1','2']
rois=['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']

# %% Pull cifti stats from text files
dest = f'{restdir}/EVO_rest_lowerlev/EVO_lowerlev_roicorrmaps_stats'

cmd = [None]
for site in sites:
    datadir = f'{maindatadir}/{site}'
    q = fmri_tools(datadir)
    for sub in q.subs:
        for roi in rois:
            roidir = f'{datadir}/{sub}/func/rois/{roi}'
            for session in sessions:
                stats_file = f'{roidir}/{sub}_{roi}_S{session}_R1_denoised_aggr_s1.7_stats.txt'
                if os.path.isfile(stats_file):
                    cmd[0] = f'cp {stats_file} {dest}'
                    q.exec_cmds(cmd)