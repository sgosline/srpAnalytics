#!/usr/bin/env python
# coding: utf-8

# In[1]:


# process phase I, II LPR (120 hrs larval photomotor response)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os, shutil, time

import warnings
warnings.filterwarnings('ignore')

import sys

#util_path = "/Users/kimd999/research/script_not_in_dropbox/srpAnalytics/analysis/latest/util"
#sys.path.insert(0, util_path)


args = sys.argv[0:]
py_file = args[0]
py_file_wo_path = os.path.basename(py_file)

code_location = os.path.dirname(os.path.abspath(py_file))
index_of_latest = code_location.index('latest')
util_path = os.path.join(code_location[:index_of_latest], "latest", "utils")
sys.path.insert(0, util_path)


# In[2]:


starting_dir = os.getcwd()
print (starting_dir)


# In[3]:


#LPR data file

#mac
#complete_file_path = '/Users/kimd999/research/projects/toxicity/per_each_data/Phase_I_II/input/behavioral/wide/Phase_I_II_wide_t0_t239_LPR_53_54_only.csv'

#constance
complete_file_path = '/people/kimd999/tox/phase_I_II/input/wide/344_zf_LPR_data_phase_1_2_2020JUNE25_updated_plate_id_for_TX_wide_t0_t239_full.csv'

lpr_all_data = pd.read_csv(complete_file_path, header = 0)


# In[4]:


print(lpr_all_data.head())
#display("lpr_all_data.shape:" + str(lpr_all_data.shape))
# Convert plate ids to ints
lpr_all_data['plate.id'] = (lpr_all_data['plate.id'].values).astype(int)
print(lpr_all_data)


# In[5]:


np.unique(lpr_all_data.well)


# In[6]:


unique_chemical_IDs = np.unique(lpr_all_data['chemical.id'])
count_wells_compounds_concentration = pd.DataFrame(columns = ['Compound', 'Concentration', 'Number_Wells'])

# Count number of wells for each chemical
for chemical_ID in unique_chemical_IDs:
    lpr_data_subset = lpr_all_data.loc[lpr_all_data['chemical.id'] == chemical_ID]
    print('\nPlates/Wells/Concentration information about compound:', chemical_ID)
    print('Plate IDs:', np.unique(lpr_data_subset['plate.id']))
    print('Number of unique plates:', len(np.unique(lpr_data_subset['plate.id'])))
    print('Concentrations tested:', np.unique(lpr_data_subset['conc']))
    print('Number of concentrations:', len(np.unique(lpr_data_subset['conc'])))
    print('Total number of wells:', lpr_data_subset.shape[0])
    for concentration_id in np.unique(lpr_data_subset['conc']):
        lpr_data_subset_concs = lpr_data_subset.loc[lpr_data_subset['conc'] == concentration_id]
        #print('Number of wells for compound ID', chemical_ID, 'and concentration', concentration_id, 'are', len((lpr_data_subset_concs['well'])))
        count_wells_compounds_concentration = count_wells_compounds_concentration.append({'Compound': chemical_ID, 'Concentration': concentration_id, 'Number_Wells': len((lpr_data_subset_concs['well']))}, ignore_index = True)


# ## Load morphological data for filtering wells that have dead fish

# In[7]:


#mac
#morph_data_file_complete_path = '/Users/kimd999/research/projects/toxicity/per_each_data/Phase_I_II/input/morphology/after_Lisa_cleanup/wide/zf_morphology_data_335_chemicals_2020DEC16_wide_DNC_0.csv'

#constance
morph_data_file_complete_path = '/people/kimd999/tox/phase_I_II/input/wide/zf_morphology_data_335_chemicals_2020DEC16_wide_DNC_0.csv'

morphology_all_data = pd.read_csv(morph_data_file_complete_path, header = 0)
print(morphology_all_data.head())


# In[8]:


# Goal of this box 
# -> (in lpr_all_data) leave only rows with non 1 and NA MORT

# 1. Append additional identifier column (Plate_Well value) to lpr and morphology data
# 2. Find rows in morphology data for which MORT end-point is not 1 or NA
# 3. Using Plate_Well values, find corresponding rows in lpr data to filter the data
lpr_all_data['Chemical_Plate_WELL'] = lpr_all_data[['chemical.id','plate.id', 'well']].apply(lambda x: '_'.join(x.map(str)), axis = 1)
morphology_all_data['Chemical_Plate_WELL'] = morphology_all_data[['chemical.id','plate.id', 'well']].apply(lambda x: '_'.join(x.map(str)), axis = 1)

morphology_nonna_data_plate_well = morphology_all_data.Chemical_Plate_WELL[~((morphology_all_data.MORT == 1) | (morphology_all_data.MORT.isnull()))]
lpr_filtered_data = lpr_all_data.loc[lpr_all_data['Chemical_Plate_WELL'].isin(list(morphology_nonna_data_plate_well.values))]

print("morphology_all_data.shape:" + str(morphology_all_data.shape))
print("morphology_nonna_data_plate_well.shape:" + str(morphology_nonna_data_plate_well.shape))

print("\nlpr_all_data.shape:" + str(lpr_all_data.shape))
print("lpr_filtered_data.shape:"+str(lpr_filtered_data.shape) + "\n")

print(morphology_nonna_data_plate_well[0:5])
print ("\n")
print(lpr_all_data.Chemical_Plate_WELL[0:5])


# In[ ]:


#(set(list(morphology_nonna_data_plate_well)) - set(list(lpr_all_data['Chemical_Plate_WELL'])))


# In[ ]:


#missmatched_data = (set(list(morphology_all_data['Chemical_Plate_WELL'])) - set(list(lpr_all_data['Chemical_Plate_WELL'])))
#with open('chemicals_difference_morph_t0_t239_behav.txt', 'w') as filehandle:
#    for listitem in missmatched_data:
#        filehandle.write('%s\n' % listitem)


# In[9]:


lpr_filtered_data.head()


# In[10]:


# Convert time resolution to minutes (if applicable)
# for LPR, 240 t something -> 24 t something

# Create a new dataframe for storing lpr data in the new time-scale (minutes)
# The new dataframe contains the same basic row identifier fields
lpr_filtered_data_in_minute = lpr_filtered_data[['chemical.id', 'conc', 'plate.id', 'well']]
print ("lpr_filtered_data_in_minute.shape:\n" + str(lpr_filtered_data_in_minute.shape)) # for lpr -> (1527, 4)
#lpr_filtered_data_in_minute.head()


time_index_sec_start = 5
max_time_index_sec = 240 # from t0 to t239

#report = True
report = False

interval = "1 min"
#interval = "30 sec"
#interval = "12 sec"
print ("interval:" + str(interval))
if (interval == "1 min"):
    group_size = 10 # (10 X 6 sec/sample = 1 min/sample)
elif (interval == "30 sec"):
    group_size = 5 # (5 X 6 sec/sample = 1 min/sample)
else: # interval = "12 sec"
    group_size = 2 # (2 X 6 sec/sample = 1 min/sample)
    
for time_index in range(int(max_time_index_sec / group_size)):
    if (report):
        print ("\ntime_index:" + str(time_index))
    
    start_index = time_index_sec_start + group_size * time_index
    if (report):
        print ("start_index:" + str(start_index))
    
    end_index = start_index + group_size
    if (report):
        print ("end_index:" + str(end_index))
    
    lpr_filtered_data_in_minutes_in_this_time_index = pd.DataFrame(np.sum(lpr_filtered_data.iloc[:,start_index:end_index], axis = 1))
    #if (report):
    #    print ("lpr_filtered_data_in_minutes_in_this_time_index.shape:\n" + str(lpr_filtered_data_in_minutes_in_this_time_index.shape))
    #    display(lpr_filtered_data_in_minutes_in_this_time_index.head())
    #    display(lpr_filtered_data_in_minutes_in_this_time_index.tail())
    
    lpr_filtered_data_in_minutes_in_this_time_index.columns = ['t' + str(time_index)]
    #lpr_filtered_data_in_minutes_in_this_time_index.columns = np.transpose(['t' + str(i) for i in range(int(max_time_index_sec / group_size))])
    lpr_filtered_data_in_minute = pd.concat([lpr_filtered_data_in_minute, lpr_filtered_data_in_minutes_in_this_time_index], axis = 1)
pd.set_option('display.max_columns', None)
print ("lpr_filtered_data_in_minute.shape:\n" + str(lpr_filtered_data_in_minute.shape)) # for lpr -> (1527, 28)
#lpr_filtered_data_in_minute.head(100) # this should have only 0~23 Tns

lpr_filtered_data_in_minute['chemical_conc'] = lpr_filtered_data_in_minute[['chemical.id','conc']].apply(lambda x: '_'.join(x.map(str)), axis = 1)
#lpr_filtered_data_in_minute.head(1000) # this should have only 0~23 Tns

#lpr_filtered_data_in_minute_groupped = lpr_filtered_data_in_minute.groupby(['chemical_conc']).sum()
lpr_filtered_data_in_minute_groupped = lpr_filtered_data_in_minute.groupby(['chemical_conc']).mean()
lpr_filtered_data_in_minute_groupped.head() # this should have only 0~23 Tns

lpr_filtered_data_in_minute_groupped.to_csv('lpr_filtered_data_in_minute_groupped.csv', index=False)


# In[ ]:


"(Lisa) LPR (5d): L1: T61-89; D1: T90-119; L2: T120-149; D2: T150-179; L3: T180-209; D3: T210-239"

# (L0,D0) 
# T1 - T60 --> 360 seconds -> 6 minutes

# (L1,D1) 
# T61 - T120 --> 360 seconds -> 6 minutes

# (L2,D2) 
# T121 - T180 --> 360 seconds -> 6 minutes

# (L3,D3) 
# T181 - T240 --> 360 seconds -> 6 minutes


# In[11]:


# Plot few lpr curves to check transition points
# Plotting to make sure that data makes sense
time_index_start = 4 # because 0-3th columns show irrelevant values
num_time_points = 24 # >= 25 will not make any difference

print ("lpr_filtered_data_in_minute.shape:" + str(lpr_filtered_data_in_minute.shape))
# lpr 1 minute interval -> (1527, 124)

fig, ax = plt.subplots()

#print (lpr_filtered_data_in_minute.iloc[10:15, time_index_start:time_index_start + num_time_points]) 
# first ':' shows rows, second ':' shows columns

ax.plot(np.transpose(lpr_filtered_data_in_minute.iloc[10:223,time_index_start:time_index_start + num_time_points].values));


# In[12]:


delta_mov_auc = lpr_filtered_data_in_minute[['chemical.id', 'conc', 'plate.id', 'well']].copy()

#transition_points = [4,10,16,22]
# middle points of each peak -> 4,10,16,22

#transition_points = [4,10,16] # using 22 caused an error
#--> results with these transition_points tend to be NA

transition_points = [2] 
#transition_points = [3] 
# following Paritosh's example, eventually 2,8,14 etc, 
# but for now (portal establishment), only the first transition is needed.

num_light = 3 # seems reasonable since interval between middle points of each peak ~= 6
num_dark  = 3

#delta_mov_auc['MOV_1_2_3'] = 0 # just initial value
#delta_mov_auc['AUC_1_2_3'] = 0 # just initial value

for transition_index, transition_point in enumerate(transition_points):
    print ("\n")
    print ("transition_index:" + str(transition_index))
    print ("transition_point:" + str(transition_point))
    
    delta_mov_auc['MOV' + str(transition_index + 1)]     = lpr_filtered_data_in_minute['t' + str(transition_point + 1)]     - lpr_filtered_data_in_minute['t' + str(transition_point)]

    delta_mov_auc['AUC' + str(transition_index + 1)]     = sum(lpr_filtered_data_in_minute['t' + str(transition_point + 1 + index_count)]           for index_count in range(num_dark))     - sum(lpr_filtered_data_in_minute['t' + str(transition_point - index_count)]           for index_count in range(num_light))
    
    # I didn't fully understand this part, but it works as intended
    #delta_mov_auc['MOV_1_2_3'] = delta_mov_auc['MOV_1_2_3'] + delta_mov_auc['MOV' + str(transition_index + 1)]
    #delta_mov_auc['AUC_1_2_3'] = delta_mov_auc['AUC_1_2_3'] + delta_mov_auc['AUC' + str(transition_index + 1)]
    
print(delta_mov_auc.head())


# In[13]:


# Rename column headers to make it compatible with earlier data received from Lisa
delta_mov_auc.rename(columns={"chemical.id": "Chemical.ID", "conc": "CONC", "plate.id": "Plate", "well": "WELL"}, inplace = True)
print(delta_mov_auc.head())


# In[14]:


print(delta_mov_auc.tail())


# In[15]:


import generate_dose_response_newest_no_avg as gdr
import BMD_BMDL_estimation as bmdest
import Plot_Save as ps


# In[16]:


start_time = time.time()
os.chdir(starting_dir)

if (os.path.isdir("output") == True):
    shutil.rmtree("output")
os.mkdir("output")

output_folder = os.path.join(starting_dir, "output")
os.chdir(output_folder)

full_devel = "full"
#full_devel = "devel"

if (full_devel == "full"):
    chemical_id_from_here = np.unique(delta_mov_auc['Chemical.ID'])
else:
    chemical_id_from_here = [53]

if (full_devel == "full"):
    end_points_from_here = ['MOV1','AUC1']
else:
    end_points_from_here = ['MOV1']
    #end_points_from_here = ['MOV1_2_3']

#report = True
report = False

for chemical_id in chemical_id_from_here:
    if (report): print("chemical_id:" + str(chemical_id))
    for end_point in end_points_from_here:
        if (report): print("end_point:" + str(end_point))
        # subset original dataframe for a user-specified chemical and end_point pair
        delta_mov_auc_end_point_chemical_id = delta_mov_auc.loc[delta_mov_auc['Chemical.ID'] == chemical_id,['Chemical.ID', 'CONC', 'Plate', 'WELL', end_point]]
        #print("delta_mov_auc_end_point_chemical_id:\n"+str(delta_mov_auc_end_point_chemical_id))
        #print("type(delta_mov_auc_end_point_chemical_id):\n"+str(type(delta_mov_auc_end_point_chemical_id)))
        #print("type(end_point):\n"+str(type(end_point)))

        dose_response = gdr.gen_dose_response_behavior(delta_mov_auc_end_point_chemical_id, end_point)
        if (report): print("dose_response:\n"+str(dose_response))
        qc_flag = gdr.BMD_feasibility_analysis(dose_response)
        test_dose_response = gdr.reformat_dose_response(dose_response)
        #test_dose_response = dose_response
        if(qc_flag in [0, 1]):
            # No BMD analysis required. Generate report and exit
            ps.save_results_poor_data_or_no_convergence(test_dose_response, qc_flag, str(chemical_id), end_point, None)
        else:
            # Fit dose response models
            model_predictions = bmdest.analyze_dose_response_data(test_dose_response)
            # Select best model
            selected_model_params = bmdest.select_model(model_predictions)
            # Check if unique model is found
            unique_model_flag = selected_model_params['no_unique_model_found_flag']
            if(unique_model_flag == 0):
                # Generate report
                ps.save_results_good_data_unique_model(test_dose_response, qc_flag, model_predictions, selected_model_params, str(chemical_id), end_point)
            else:
                bmd_analysis_flag = selected_model_params['model_select_flag']
                if(bmd_analysis_flag == 1):
                    ps.save_results_poor_data_or_no_convergence(test_dose_response, qc_flag, str(chemical_id), end_point, selected_model_params)
                else:
                    ps.save_results_good_data_nounique_model(test_dose_response, qc_flag, model_predictions, selected_model_params, str(chemical_id), end_point)
end_time = time.time()
time_took = str(round((end_time-start_time), 1)) + " seconds"
print ("Done, it took:"+str(time_took))
# 1 chemical (3756) and 2 endpoints (['MOV1','AUC1']), 140 seconds took
# 7 chemicals and 2 endpoints (['MOV1','AUC1']), 6 minutes took

time_filename = 'running_time.txt'
f_time = open(time_filename, 'w')
f_time.write(str(time_took))
f_time.close()


# In[ ]:




