# EVO Higher-Level ROI Analysis
# Higher-level modeling with cifti stats from text files

# Holland Brown

# Updated 2023-12-02
# Created 2023-12-01

# ---------------------------------------------------------------------------------------------------------------

# %%
import os
import glob
from my_imaging_tools import fmri_tools

sites = ['NKI','UW']

# q = fmri_tools(datadir)
sessions = ['1','2']
rois=['L_MFG','R_MFG','L_dACC','R_dACC','L_rACC','R_rACC']

# %% Pull cifti stats text files from subject ROI dirs
maindatadir = f'/athena/victorialab/scratch/hob4003/study_EVO' # where subject folders are located
restdir = f'/athena/victorialab/scratch/hob4003/study_EVO/EVO_rest' # where to create folder of cifti stats txt files
wb_command = f'/software/apps/Connectome_Workbench_test/workbench/exe_rh_linux64/wb_command' # /path/to/wb_command package
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

# %% Extract cifti stats from text files
stats_file_dir = f'/home/holland/Desktop/EVO_lowerlev_roicorrmaps_stats'

for roi in rois:
    for session in sessions:
        roi_stats_files = glob.glob(f'{stats_file_dir}/*{roi}_S{session}*.txt')
        for roi_stats_file in roi_stats_files:
            
            # init dictionary
            roi_stats_dict = {
                'stdev':[],
                'variance':[],
                'sampstdev':[],
                'tsnr':[],
                'cov':[],
                'l2norm':[],
                'max':[],
                'min':[]
            }
            
            # read stats file
            f = open(roi_stats_file, 'r')
            stats = f.readlines()
            f.close()

            # save stats from file in dict lists
            roi_stats_dict['stddev'].append(stats[1])
            roi_stats_dict['variance'].append(stats[5])
            roi_stats_dict['sampstdev'].append(stats[9])
            roi_stats_dict['tsnr'].append(stats[13])
            roi_stats_dict['cov'].append(stats[17])
            roi_stats_dict['l2norm'].append(stats[21])
            roi_stats_dict['max'].append(stats[25])
            roi_stats_dict['min'].append(stats[29])

            for key in roi_stats_dict:
                




