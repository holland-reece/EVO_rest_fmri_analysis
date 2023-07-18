# Visualize EVO lower-level analysis results

# Holland Brown

# Updated 2023-05-09
# Created 2023-03-29


#--------------------------------------------------
# %% Define functions
def read_sublist(subjlist):
    s = open(subjlist,'r') # open subject list text file in read mode
    subjs = s.readlines() # create list of string objects
    s.close() # close text file
    subjs = [el.strip('\n') for el in subjs] # remove newline characters from list
    subjs = [el.strip(' ') for el in subjs] # remove space characters from list
    return subjs

def exec_cmds(commands): # run commands in system terminal (must be bash terminal, and function input must be list)
    for command in commands:
        subprocess.run(command, shell=True, executable='/bin/bash') # run command in bash shell
        
# Setup 1: import modules; set environment, directories, and paths
import subprocess
import glob
import os
# import pyPdf
# from xhtml2pdf import pisa

operating_system = 1 # Linux (0) or MacOS (1)
roi = 'L_rACC' # name of ROI mask, will be used to create directories and Feat design file
# feat_fn = '20230418_lower_lev_gsr_remean.fsf' # FeatFileName.fsf
sublist_tf = f'bad_registration.txt' # SubjectListName.txt
# preproc_folder = 'rest_afni_results_ICA' # PreprocessedInputsFolder -> omit subject ID from beginning, will look like dir/<subjectID>_PreprocessedInputsFolder
# nifti_fn = 'gsr_fanat.nii.gz' # name of nifti file after global signal regression
# roi_tn = 'gsr_remean.txt' # leave out roi name and underscore -> roi_tn will be concatenated w roi name, so you can just make it '.txt'
feat_folder = 'rest.feat' # FeatFolderName (not a directory)
check_statfiles = ['zstat.nii.gz','cope1.nii.gz','varcope1.nii.gz'] # list stats files you want to check exist for all subs (if running check_files_present)
# QAfiles = ['design.png','design_cov.png','rendered_thresh_zstat1.png'] # QA html or png files to be concatenated (if running cat_html)
QA_out_fn = f'{roi}_lower_lev_gsr_remean' # QAsummaryFileName (omitt extension)

# LINUX DIRECTORIES
if operating_system == 0:
    datadir = '/media/holland/LACIE-SHARE/EVO_MRI_data' # main data directory
    sublist = f'/media/holland/LACIE-SHARE/EVO_MRI_data/{sublist_tf}' # full/path/to/subjectlist.txt

# MAC DIRECTORIES
elif operating_system == 1:
    datadir = '/Volumes/LACIE-SHARE/EVO_MRI_data' # main data directory
    sublist = f'/Volumes/LACIE-SHARE/EVO_MRI_data/{sublist_tf}' # full/path/to/subjectlist.txt


# Setup 2: user options (0 to skip, 1 to run)
check_files_present = 0
search_logs = 0
cat_html = 1 # concatenate analysis output html files into one
html2pdf = 0 # convert html file into a pdf (html files depend on local directories -> convert to pdf to view elsewhere)
ran_Feat_lower_level = True # set to True if you ran lower level Feat analysis -> want to include design matrices, z-score activation maps in html output (o.t. set False)


# %% Code main body
subs = read_sublist(sublist) # read sublist text file into list necessary for all/any subsequent steps
print(subs)


# Check all files are present after analysis
if check_files_present == 1:
    for statfile in check_statfiles:
        files_list = glob.glob(f'{datadir}/*/{roi}/{feat_folder}/stats/{statfile}')
        if len(files_list) != len(subs):
            print(f"{statfile} files do not exist for all subjects...")


# Search FSL report logs for error and warning messages
if search_logs == 1:
    cmds = []
    log_strings = ['error','Error','ERROR','warning','Warning','WARNING']
    for sub in subs:
        for string in log_strings:
            cmds[0] = f'grep "{string}" {datadir}/{sub}/{roi}/{feat_folder}/report_log.html' # search log for a string value
            exec_cmds(cmds)

# Concatenate analysis output html files
if cat_html == 1:

    # Create a summary html file
    s = open(f'{datadir}/{QA_out_fn}.html','w')
    for sub in subs:
        filedir = f'{datadir}/{sub}/{roi}/{feat_folder}'
        preprocdir = f'{datadir}/{sub}/rest/rest_preproc.feat'
        s.write(f"Subject: {sub}")

        # Preprocessing QC images
        if os.path.exists(f'{preprocdir}/reg/example_func2highres.png'):
            s.write("<IMG SRC=\"%s/reg/example_func2highres.png\" WIDTH=1600>"%(preprocdir)) # reg functional to highres (anatomical) image
        if os.path.exists(f'{preprocdir}/reg/example_func2standard.png'):
            s.write("<IMG SRC=\"%s/reg/example_func2standard.png\" WIDTH=1600>"%(preprocdir)) # reg functional to standard space
        if os.path.exists(f'{preprocdir}/reg/highres2standard.png'):
            s.write("<IMG SRC=\"%s/reg/highres2standard.png\" WIDTH=1600>"%(preprocdir)) # reg highres (anatomical) to standard space

        # Lower level Feat analysis QC images
        if ran_Feat_lower_level == True:
            if os.path.exists(f'{filedir}/rendered_thresh_zstat1.png'):
                s.write("<IMG SRC=\"%s/rendered_thresh_zstat1.png\" WIDTH=1000>"%(filedir)) # z-score activation map
            if os.path.exists(f'{filedir}/design.png'):
                s.write("<IMG SRC=\"%s/design.png\">"%(filedir)) # analysis design matrix
            if os.path.exists(f'{filedir}/design_cov.png'):
                s.write("<IMG SRC=\"%s/design_cov.png\" >"%(filedir)) # analysis design covariance
    s.close()

# %% FIX: Convert html to pdf
# CAN'T GET THIS TO WORK; REQUIRES EXTENSIVE CODING IN html
# ended up just taking screenshots, converting them to pdf files and combining them in MacOS Previewer, but doing it that way SUCKS!

# if html2pdf == 1:
#     source_html = f'<{datadir}/{QA_out_fn}.html><body><p>' # define input html
#     output_filename = f'{QA_out_fn}.pdf' # define output pdf file name

#     # Utility function
#     def convert_html_to_pdf(source_html, output_filename):
#         result_file = open(output_filename, "w+b") # open output file for writing (truncated binary)
#         pisa_status = pisa.CreatePDF(
#                 source_html,                # the HTML to convert
#                 dest=result_file)           # file handle to recieve result
#         result_file.close()                 # close output file
#         return pisa_status.err # return False on success and True on errors

#     # Main program
#     if __name__ == "__main__":
#         pisa.showLogging()
#         convert_html_to_pdf(source_html, output_filename)
