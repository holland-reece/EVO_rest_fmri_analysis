"""
EVO resting-state group-level 2-way mixed effects ANOVA using ROI-to-whole brain within-subject COPEs

Updated: 2024-05-16
Created: 2024-05-13

# Description:
    - Create directories and rename files in subject dirs so group level models can be run in Feat (without having run registration in Feat)
    - Run Feat group level 2-way mixed effects ANOVAs for all ROIs in parallel (need fsf files for each ROI ready)

"""

# %% Set up dirs and import packages
import glob
import subprocess
from multiprocessing import Pool
from my_imaging_tools import fmri_tools

def process_system_task(args):
    """
    - called in main()
    - takes arguments from main() and runs hands bash command strings to system to execute
    """
    home_dir, roi, update_string = args
    print(update_string)
    cmd[0] = f'feat {home_dir}/EVO_rest_higherlev_vol/{roi}_grouplevel.fsf'
    subprocess.run(cmd, shell=True, executable='/bin/bash')

def main():
    """
    - define class main()
    - first, creates args to hand off to function process_system_task
    - second, calls function process_system_task using Pool to parallelize
    """
    bash_commands = [] # preallocate list of commands to execute in parallel
    for roi in rois:
        update_str = f'Running group-level Feat model for {roi}...'
        bash_commands.append((grouplev_dir, roi, update_str)) # append all args needed for one call to process_system_task()

    with Pool(processes=len(rois)) as pool:
        pool.map(process_system_task, bash_commands)
        pool.close()
        pool.join()


home_dir = f'/Volumes/EVO_Estia' # path to HDD
datadir = f'{home_dir}/EVO_MRI/organized/UW' # where subject dirs are located
fsldir = f'/Users/amd_ras/fsl' # where FSL is installed in your system
q = fmri_tools(datadir) # init class containing functions to execute bash commands

# %% Make /reg dir in all lower-level Feat dirs (needed for Feat group level)
cmd = [None]*3
dirs = glob.glob(f'{datadir}/*/func/rest/rois/*/rest_lowerlev_vol/*.feat')
for dir in dirs:
    cmd[0] = f'mkdir {dir}/reg' # create /reg dir
    cmd[1] = f'cp {dir}/mean_func.nii.gz {dir}/reg' # copy mean_func into /reg
    cmd[2] = f'mv {dir}/reg/mean_func.nii.gz {dir}/reg/standard.nii.gz' # rename mean_func to what Feat expects


    q.exec_cmds(cmd)

# %% Copy identity matrix into new /reg dirs
# NOTE: ident.mat should be in $FSLDIR/etc/flirtsch/ident.mat, wherever that is on your machine
cmd = [None]
dirs = glob.glob('/Volumes/EVO_Estia/EVO_MRI/organized/NKI/*/func/rest/rois/*/rest_lowerlev_vol/*.feat/reg')
for dir in dirs:
    cmd[0] = f'cp /Users/amd_ras/fsl/etc/flirtsch/ident.mat /{dir}/example_func2standard.mat'
    q.exec_cmds(cmd)

# %% Run all group-level Feat models in parallel
# NOTE: left out L_dACC because I used L_dACC to test the Feat model first

rois = ['L_MFG','R_MFG','L_rACC','R_rACC','R_dACC']
grouplev_dir = f'{home_dir}/EVO_rest_grouplevel_volume/grouplevel_models_v2_feat-mixedeffects_anova'

# Execute all group-level Feat models in parallel
if __name__ == '__main__':
    main()

# %%
