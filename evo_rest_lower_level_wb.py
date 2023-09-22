# EVO Lower-level ROI analysis - Connectome Workbench version

# Holland Brown

# Updated 2023-09-22
# Created 2023-09-22

#---------------------------------------------------------------------------------------------------------------

# %%
import tqdm
import json
from my_imaging_tools import fmri_tools
from nipype import Node, Function
from nipype.interfaces.workbench.cifti import WBCommand

datadir = f''

q = fmri_tools(datadir)
sessions = ['1','2']

# %% Create Nipype workflow



# %% ROI-to-wholebrain correlation
# https://www.humanconnectome.org/software/workbench-command/-cifti-average-roi-correlation

for sub in q.subs:

    # get TR from JSON
    with open(f'{datadir}/{sub}/func/unprocessed/session_1/run_1/Rest_S1_E1_R1.json', 'rt') as rest_json:
        rest_info = json.load(rest_json)
    TR = rest_info['RepetitionTime']

    for s in sessions:
        subdir = f'{datadir}/{sub}/func/rest/session_{s}/run_1'
        
        

