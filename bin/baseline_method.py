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
import warnings
warnings.filterwarnings('ignore')
# import useful functions
sys.path.append('../')
from src.utilities import utility_matrix

start_time = time.monotonic()

#####################
# parameter setting #
#####################

# all the arguments must be passed, the order IS relevant
if len(sys.argv) == 4: # NB: 4 because argv[0] is the name of the script
    # dataset path
    data_path = str(sys.argv[1])
    # patient ID
    patient_id = str(sys.argv[2])
    # condition ID
    cond_id = str(sys.argv[3])
    print("> Parameters setted")
else:
    # Default parameters if nothing is passed
    data_path = '../data/full_data.json'
    patient_id = "pat_0"
    cond_id = "cond_0"
    
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

# patient_id = "pat_6"
# cond_id = "cond_2"
cond = conditions_df[conditions_df.id == cond_id].name.values[0] 

################################
# reccomand therapies using CF #
################################
def baseline_method(data, patient_id, cond_id):
    reccomended_ther = pd.DataFrame(columns = ['id', 'name', 'type'])

    # open dataset
    # with open(dataset_path, 'r') as file:
    #     data = json.load(file)
    patients_df = pd.DataFrame(data['Patients'])
    conditions_df = pd.DataFrame(data['Conditions'])
    therapies_df = pd.DataFrame(data['Therapies'])
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
                # ther_row['details'] = f"cured with success on itself" 
                reccomended_ther = reccomended_ther.append(ther_row, ignore_index = True)
                #return reccomended_ther
            # else:
            # find cured patients subset
            pat_cured = []
            for i in patients_df.id.values:
                if any(d['kind'] == cond_id and d['cured'] != None for d in patients_df[patients_df.id == i].conditions.values[0]):
                    #print(i)
                    
                    pat_cured.append(i)
            # build patient utility matrix
            patient_id_u_mat = utility_matrix(patient_id).to_numpy()
            # build cured patient utility matrix and calculate cosine similarity with patient id matrix
            cosine_sim = []

            for i in tqdm(pat_cured, desc="Caclulating cosine distances"):
                cured_u_mat = utility_matrix(i).to_numpy()
                cosine_sim_pat = 1 - distance.cosine(patient_id_u_mat.flatten(), cured_u_mat.flatten())
                cosine_sim.append(cosine_sim_pat)
            
            cos_sim_df = pd.DataFrame({"pat_cured" : pat_cured, 
                "cosine_similarity": cosine_sim})
            cos_sim_df_sort = cos_sim_df.sort_values("cosine_similarity", ascending=False)
            
            # extract therapies that cured the most similar patients
            for pat in cos_sim_df_sort.pat_cured.values:
                if len(reccomended_ther) < 5:
                    succ_cond_id = list(filter(lambda d: d['kind'] == cond_id, patients_df[patients_df.id == pat].conditions.values[0]))[0]['id'] 
                    ther_id = list(filter(lambda d: d['condition'] == succ_cond_id and d['successful']>90, patients_df[patients_df.id == pat].trials.values[0]))[0]['therapy']
                    
                    # similarity = cos_sim_df_sort[cos_sim_df_sort.pat_cured == pat]['cosine_similarity'].values[0]
                    ther_row = therapies_df[therapies_df.id == ther_id]
                    # ther_row['details'] = f"cured with success on {pat} ({similarity} cosine similarity with {patient_id})" 
                    # add only therapies that are not in the reccomandation yet
                    if ther_id not in reccomended_ther.id.values:
                        reccomended_ther = reccomended_ther.append(ther_row, ignore_index = True)

    return reccomended_ther

# execute the function                
res = baseline_method(data, patient_id, cond_id)   

end_time = time.monotonic()
tot_time = timedelta(seconds=end_time - start_time)

# save the results 
count = 1
with open("../results/baseline_eval.txt", 'a') as f:
        f.write(f"Output for 'python baseline_method.py {data_path } {patient_id} {cond_id})'\n > Recommended therapies for {patient_id} to treat condition {cond}: \n")
        for idx,row in res.iterrows():
            name = res[res.id == row.id].name.values[0]
            f.write(f"{count}^: {row.id}  |  {name}  |  {row.type} \n")
            count += 1
        f.write("-----------------------------------------------------------------------------------------------------------------------------------------\n")
        f.write(f"Time of program execution: {tot_time}\n")
        f.write("-----------------------------------------------------------------------------------------------------------------------------------------\n")

print("> Results and execution time are stored in 'results/results.txt' file")

            