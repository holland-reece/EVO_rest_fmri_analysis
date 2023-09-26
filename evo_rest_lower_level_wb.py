# EVO Lower-level ROI analysis - Nipype/Connectome Workbench version

# Holland Brown

# Updated 2023-09-22
# Created 2023-09-22

# Next:
    # add read_json function to my_imaging_tools module (started)

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

# %% Specify Nipype nodes

# Level1Design - Generates an SPM design matrix
level1design = Node(Level1Design(bases={'hrf': {'derivs': [1, 0]}},
                                 timing_units='secs',
                                 interscan_interval=TR,
                                 model_serial_correlations='FAST'),
                    name="level1design")

# EstimateModel - estimate the parameters of the model
level1estimate = Node(EstimateModel(estimation_method={'Classical': 1}),
                      name="level1estimate")

# EstimateContrast - estimates contrasts
level1conest = Node(EstimateContrast(), name="level1conest")





# %% ROI-to-wholebrain correlation
# https://www.humanconnectome.org/software/workbench-command/-cifti-average-roi-correlation

for sub in tqdm(q.subs):

    # get TR from JSON
    with open(f'{datadir}/{sub}/func/unprocessed/session_1/run_1/Rest_S1_E1_R1.json', 'rt') as rest_json:
        rest_info = json.load(rest_json)
    TR = rest_info['RepetitionTime']

    for s in sessions:
        subdir = f'{datadir}/{sub}/func/rest/session_{s}/run_1'
        
        

