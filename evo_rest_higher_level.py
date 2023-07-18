# EVO Higher-level Analysis: Baseline to post-intervention

# Holland Brown

# Updated 2023-04-03
# Created 2023-03-20

# Source: Nili's/Lauren's runhigherlevel_HRSD.sh from Engage study

#----------------------------------------------------------------------------------------
# %% Define functions
def read_sublist(subjlist):
    s = open(subjlist,'r') # open subject list text file in read mode
    subjs = s.readlines() # create list of string objects
    s.close() # close text file
    subjs = [el.strip('\n') for el in subjs] # remove whitespace characters from list
    return subjs

def exec_cmds(commands): # run all commands for one subject
    for command in commands:
        try:
            subprocess.run(command, shell=True)
        except OSError as system_err:
            print(system_err)

# %% Setup 1: import modules; set environment, directories, and paths
import subprocess

# datadir = '/media/holland/LACIE-SHARE/EVO_MRI_data' # main data directory
# sublist = '/media/holland/LACIE-SHARE/EVO_MRI_data/sublist_part.txt' # full/path/to/subjectlist.txt
datadir = '/Volumes/LACIE-SHARE/EVO_MRI_data' # main data directory
sublist = '/Volumes/LACIE-SHARE/EVO_MRI_data_TEST/sublist_TEST.txt' # full/path/to/subjectlist.txt
roi = 'Left_MFG' # roi (should be same format as roi folder name)

roi = 'Left_MFG' # ROI to be analyzed (should be same as roi file name without the extension)
feat_df = f'/home/holland/Desktop/evo_ana_scripts/evo_fsf/{roi}_lower_level.fsf' # feat design file with full extension (need this for Step 4)

# %% Setup 2: User options
flameo = 1
randomise = 0

# %% Setup 3: Create subs list and make QC dir
subs = read_sublist(sublist) # read subject list file into a list object
if subs[-1]=='' or subs[-1]=='\n': # if there's whitespace at the end, remove it
    subs.pop(-1)

# %% Combine copes and varcopes


# %% Flameo
if flameo==1:
    cmds = ['','']
    for sub in subs:
        # flameo --cope=fixed_effects/cope_merge --varcope=fixed_effects/varcope_merge --mask=${templates2} --dm=../BADS.mat --tc=../BADS.con --cs=../HRSD.grp --runmode=flame1 --logdir=${roi}_BADS_improvement
	    # cmd[0] = f"flameo --cope=cope1_perc --mask=${templates2} --dm=../HRSD_2way.mat --tc=../HRSD_2way.con --cs=../group.grp --runmode=flame1 --logdir=${roi}_HRSD_2way"
        exec_cmds(cmds)

# %% Randomise
if randomise==1:
    cmds = ['']
    for sub in subs:
        cmds[0] = f"randomise -i Left_InsulaCopes_4Dmerged.nii.gz -o left_insula_c -m MNI152_T1_2mm_brain_mask.nii.gz -d GroupDiff.mat -t GroupDiff.con -e GroupDiff.grp -x -T -R –uncorrp "
        exec_cmds(cmds)
