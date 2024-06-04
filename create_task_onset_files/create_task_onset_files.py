# EVO Task-Based fMRI: Create Task Onset Text Files as Expected by FSL Feat

# Holland Brown

# Updated 2024-06-04
# Created 2024-06-03

# NOTE: refer to Oded Bein's jupyter notebook for creating task onset files
    # see Oded's example onset file for a task with 16 conditions

# NOTE: for EVO study's Floop (Stroop with Flankers) task, there are 4 conditions

""" Oded's notes about his code:

So, this is actually an overly complicated script bc in that experiment we had 16 trials, 
and there were bugs in the code that ran the study and how it logged in participants misses/errors
(data collected before I joined the lab, you can see I have experience with taking over projects  ). 
The thing I think that is most relevant to you is this function:

create_all16states_onsets

and the loop in the chunk called "Create onsets for all subjects, all 16 states model". The loops 
takes in a behavioral file per participant, then split it to runs because in my study, all runs were 
saved in one behaivoral file, and then calls the function above.
 
In the function "create_all16states_onsets", there's a lot of junk you won't need. But basically
"states" in that code are the different conditions, so it created a file per each state, and then 
a file for errors. I think the most relevant parts are the beginning where I define some things, and 
then the loop under:

### for each state, create onsets file:
And you can see how I created the trash regressor in addition to a file per state/condition.

Also note that I used RTs as the duration column. I'll ask Lindsay whether the duration should be 
the trial duraion or the RT, as this is task dependent. I also attach a behavior file if it's useful 
to understand the code.

"""

# --------------------------------------------------------------------------------------
# %%
import os
import subprocess
import numpy as np
import pandas as pd
import os
import csv
import warnings
from scipy.io import loadmat
import scipy.stats as stats
import glob
import math
from my_imaging_tools import fmri_tools

# Define functions
def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier

#set pandas option:
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

# Important dirs
# home_dir = f'/media/holland/EVO_Estia/EVO_MRI/organized' # path to MNI brain template for FSL, fsf file, etc
home_dir = f'/Volumes/EVO_Estia/EVO_MRI/organized' # path to MNI brain template for FSL, fsf file, etc
onset_excel_path = f'' # dir containing excel files with onset times for each subject

sessions = ['1','2'] # for Floop, there are 2 sessions (for most participants)
runs = ['1','2'] # for Floop, there are 2 runs
sites = ['NKI','UW'] # collection sites (also names of dirs)
task_name = 'floop' # task name as it appears in directories

# %%
command = [None]*2
for site in sites:
    datadir = f'{home_dir}/{site}'
    q = fmri_tools(datadir)
    for sub in q.subs:
        for session in sessions:
            for run in runs:
                onsetfile_path = f'{datadir}/{sub}/func/unprocessed/task/{task_name}/session_{session}/run_{run}'
                command[0] = f'touch {onsetfile_path}/{task_name}_S{session}_R{run}_onset.txt' # create empty text file
