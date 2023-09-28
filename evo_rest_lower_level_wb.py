# EVO Lower-level ROI analysis - Nipype/Connectome Workbench version

# Holland Brown

# Updated 2023-09-26
# Created 2023-09-22

# Next:
    # add read_json function to my_imaging_tools module (started)
    # use Nipype to execute Connectome Workbench commands (for now, use exec_cmds)

#---------------------------------------------------------------------------------------------------------------

# %%
import tqdm
import json
from my_imaging_tools import fmri_tools
# from nipype import Node, Function
# from nipype.interfaces.workbench.cifti import WBCommand

datadir = f''

q = fmri_tools(datadir)
sessions = ['1','2']

# %% Specify Nipype nodes

# # Level1Design - Generates an SPM design matrix
# level1design = Node(Level1Design(bases={'hrf': {'derivs': [1, 0]}},
#                                  timing_units='secs',
#                                  interscan_interval=TR,
#                                  model_serial_correlations='FAST'),
#                     name="level1design")

# # EstimateModel - estimate the parameters of the model
# level1estimate = Node(EstimateModel(estimation_method={'Classical': 1}),
#                       name="level1estimate")

# # EstimateContrast - estimates contrasts
# level1conest = Node(EstimateContrast(), name="level1conest")





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

cmd = [None]*2
for sub in tqdm(q.subs):

    # get TR from JSON
    with open(f'{datadir}/{sub}/func/unprocessed/session_1/run_1/Rest_S1_E1_R1.json', 'rt') as rest_json:
        rest_info = json.load(rest_json)
    TR = rest_info['RepetitionTime']

    for s in sessions:
        subdir = f'{datadir}/{sub}/func/rest/session_{s}/run_1'

        cifti_out = f''
        cmd[0] = f'wb_command -cifti-average-roi-correlation <cifti-out> - output - output cifti file'
        
        

