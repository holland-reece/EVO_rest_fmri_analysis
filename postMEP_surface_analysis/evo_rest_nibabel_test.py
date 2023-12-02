# From Nibabel tutorial, NeuroHackademy 2020
# https://github.com/neurohackademy/nh2020-curriculum/blob/master/we-nibabel-markiewicz/NiBabel.ipynb

# %%
import nibabel as nb
print(nb.__version__)

# %% Some additional, useful imports
from pathlib import Path              # Combine path elements with /
from pprint import pprint             # Pretty-printing

import numpy as np                    # Numeric Python
from matplotlib import pyplot as plt  # Matlab-ish plotting commands
from nilearn import plotting as nlp   # Nice neuroimage plotting
import transforms3d                   # Work with affine algebra
from scipy import ndimage as ndi      # Operate on N-dimensional images
import nibabel.testing                # For fetching test data

%pylab inline