############
# SETTINGS #
############
# import libraries

import pandas as pd
import json
from tqdm import tqdm
import sys
import scipy.spatial.distance as distance
import time
from datetime import timedelta
import os.path
from os import path
import warnings
import sys
warnings.filterwarnings('ignore')
# import useful functions
sys.path.append('../')
from src.utilities import utility_matrix

#####################
# parameter setting #
#####################

# all the arguments must be passed in the right order
if len(sys.argv) == 5: # NB: 4 because argv[0] is the name of the script
    # dataset path
    data_path = str(sys.argv[1])
    # patient ID
    patient_id = str(sys.argv[2])
    # condition ID
    cond_id = str(sys.argv[3])
    # if it is a test
    test = str(sys.argv[4])
    print("> Parameters setted")
else:
    # Default parameters if nothing is passed
    data_path = '../data/full_data.json'
    patient_id = "pat_0"
    cond_id = "cond_0"
    test = "single_run"
    
####################
# parameters check #
####################
if path.exists(data_path) == False:
    sys.exit("Dataset path does not exist, try with '../data/full_data.json'")

############################################
# open dataset and define global variables #
############################################
# open json data
with open(data_path, 'r') as file:
    data = json.load(file)

# define useful variable
conditions_df = pd.DataFrame(data['Conditions'])
therapies_df = pd.DataFrame(data['Therapies'])
patients_df = pd.DataFrame(data['Patients'])  

# check on patient and condition id parameter
if patient_id not in patients_df.id.values:
    sys.exit("Patient ID is not in the data")
if cond_id not in conditions_df.id.values:
    sys.exit("Condition is not in the data")

# extract condition value
cond = conditions_df[conditions_df.id == cond_id].name.values[0]
    
################################
# reccomand therapies using CF #
################################

def my_program2(data, patient_id, cond_id):
    reccomended_ther = pd.DataFrame(columns = ['id', 'name', 'type'])

    # check if patients and condition exists
    if patient_id not in patients_df.id.values:
        print("Patient ID is not in the data")
    else:
        if cond_id not in conditions_df.id.values:
            print("Condition is not in the data")
        else:
            # check if condition was already succesfully cured by a therapy (for the given patient)
            if any(d['kind'] == cond_id and d['cured'] != None for d in patients_df[patients_df.id == patient_id].conditions.values[0]):
                
                succ_cond_id = list(filter(lambda d: d['kind'] == cond_id, patients_df[patients_df.id == patient_id].conditions.values[0]))[0]['id'] 
                ther_id = list(filter(lambda d: d['condition'] == succ_cond_id and d['successful']>90, patients_df[patients_df.id == patient_id].trials.values[0]))[0]['therapy']

                ther_row = therapies_df[therapies_df.id == ther_id]
                reccomended_ther = reccomended_ther.append(ther_row, ignore_index = True)  

            # find condition's patients subset
            print(f"> Find {cond_id} cured patients subset")
            pat_cured = []
            for pat in patients_df.id.values:
                if any(d['kind'] == cond_id and d['cured'] != None for d in patients_df[patients_df.id == pat].conditions.values[0]):
                    
                    pat_cured.append(pat)
            # find candidate therapies that patients tried
            candidates_ther = [] 
            successful = []       
            for pat in pat_cured:
                # extract each patient's therapy info
                succ_cond_id = list(filter(lambda d: d['kind'] == cond_id, patients_df[patients_df.id == pat].conditions.values[0]))[0]['id'] 
                ther_id = list(filter(lambda d: d['condition'] == succ_cond_id and d['successful']>90, patients_df[patients_df.id == pat].trials.values[0]))[0]['therapy']
                success = list(filter(lambda d: d['condition'] == succ_cond_id and d['successful']>90, patients_df[patients_df.id == pat].trials.values[0]))[0]['successful']
                successful.append(success)
                candidates_ther.append(ther_id)
            # build input patient utility matrix
            patient_id_u_mat = utility_matrix(patient_id, data).to_numpy()
            
            # build condition's patients utility matrix and calculate cosine similarity with input patient matrix
            cosine_sim = []
            for i in tqdm(pat_cured, desc="Calculating cosine distances"):
                cured_u_mat = utility_matrix(i, data).to_numpy()
                cosine_sim_pat = 1 - distance.cosine(patient_id_u_mat.flatten(), cured_u_mat.flatten())
                cosine_sim.append(cosine_sim_pat)
            
            # build a dataframe containing condition's patients cosine similarity with input patients, their therapy's info
            # and the weighted rate
            cos_sim_df = pd.DataFrame({"pat_cured" : pat_cured, 
                "cosine_similarity": cosine_sim, "candidate_therapy": candidates_ther, "successful": successful})
            cos_sim_df['weighted_rate'] = cos_sim_df["cosine_similarity"] * cos_sim_df["successful"]
            cos_sim_df_sort = cos_sim_df.sort_values("weighted_rate", ascending=False)
            
            # compose the final rank list
            print("> Compose recommended therapies ranking list")
            for ther in cos_sim_df_sort.candidate_therapy.values:
                if len(reccomended_ther) < 5:
                    # add only therapies that are not in the reccomandation yet
                    if ther not in reccomended_ther.id.values:
                        ther_row = therapies_df[therapies_df.id == ther]
                        reccomended_ther = reccomended_ther.append(ther_row, ignore_index = True)
    
    return reccomended_ther


start_time = time.monotonic()
# execute the function                
res = my_program2(data, patient_id, cond_id)   
end_time = time.monotonic()
tot_time = timedelta(seconds=end_time - start_time)

# show in terminal
print("Recommended therapies ranking:")
count = 1
for idx,row in res.iterrows():
    name = res[res.id == row.id].name.values[0]
    print(f"{count}^: {row.id}  |  {name}  |  {row.type} \n")
    count += 1
print("-----------------------------------------------------------------------------------------------------------------------------------------\n")
print(f"Time of program execution: {tot_time} \n")
print("-----------------------------------------------------------------------------------------------------------------------------------------\n")

    

# save the results 
count = 1
n_patients = len(patients_df)
if test == "test":
    with open("../results/test.txt", 'a') as f:
        f.write(f"Output for 'python ther_recommendation.py {data_path } {patient_id} {cond_id}'\n > Recommended therapies for {patient_id} to treat condition '{cond}': \n")
        for idx,row in res.iterrows():
            name = res[res.id == row.id].name.values[0]
            f.write(f"{count}^: {row.id}  |  {name}  |  {row.type} \n")
            count += 1
        f.write("-----------------------------------------------------------------------------------------------------------------------------------------\n")
        f.write(f"Time of program execution: {tot_time} \n")
        f.write("-----------------------------------------------------------------------------------------------------------------------------------------\n")
    print("> Results and execution time are stored in results/test.txt")
elif test =="baseline_evaluation":
    with open("../results/baseline_eval.txt", 'a') as f:
            f.write(f"Output for 'python ther_recommendation.py {data_path } {patient_id} {cond_id}'\n > Recommended therapies for {patient_id} to treat condition '{cond}': \n")
            for idx,row in res.iterrows():
                name = res[res.id == row.id].name.values[0]
                f.write(f"{count}^: {row.id}  |  {name}  |  {row.type} \n")
                count += 1
            f.write("-----------------------------------------------------------------------------------------------------------------------------------------\n")
            f.write(f"Time of program execution: {tot_time} \n")
            f.write("-----------------------------------------------------------------------------------------------------------------------------------------\n")
    print("> Results and execution time are stored in results/baseline_eval.txt")
elif test =="single_run":
    with open("results.txt", 'a') as f:
            f.write(f"Output for 'python ther_recommendation.py {data_path } {patient_id} {cond_id}'\n > Recommended therapies for {patient_id} to treat condition '{cond}': \n")
            for idx,row in res.iterrows():
                name = res[res.id == row.id].name.values[0]
                f.write(f"{count}^: {row.id}  |  {name}  |  {row.type} \n")
                count += 1
            f.write("-----------------------------------------------------------------------------------------------------------------------------------------\n")
            f.write(f"Time of program execution: {tot_time} \n")
            f.write("-----------------------------------------------------------------------------------------------------------------------------------------\n")
    print("> Results and execution time are stored in results.txt")
elif test =="scalability_test":
    with open("../results/scalability_test.txt", 'a') as f:
            f.write("-----------------------------------------------------------------------------------------------------------------------------------------\n")
            f.write(f"Output for 'python ther_recommendation.py {data_path } {patient_id} {cond_id}'\n > Recommended therapies for {patient_id} to treat condition '{cond}' ({n_patients} patients dataset): \n")
            for idx,row in res.iterrows():
                name = res[res.id == row.id].name.values[0]
                f.write(f"{count}^: {row.id}  |  {name}  |  {row.type} \n")
                count += 1
            f.write("-----------------------------------------------------------------------------------------------------------------------------------------\n")
            f.write(f"Time of program execution: {tot_time} for {n_patients} patients \n")
            f.write("-----------------------------------------------------------------------------------------------------------------------------------------\n")
    print("> Results and execution time are stored in results/scalability_test.txt")


