############
# SETTINGS #
############
# import libraries

import pandas as pd
import requests
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
import sys
import scipy.spatial.distance as distance
import warnings
warnings.filterwarnings('ignore')
# import useful functions
sys.path.append('../')
from src.utilities import utility_matrix_single_p


############################################
# open dataset and define global variables #
############################################
# open json data
with open('../data/full_data.json', 'r') as file:
    data = json.load(file)

# define useful variable
conditions_df = pd.DataFrame(data['Conditions'])
therapies_df = pd.DataFrame(data['Therapies'])
patients_df = pd.DataFrame(data['Patients'])  

patient_id = "pat_6"
cond_id = "cond_2"
cond = conditions_df[conditions_df.id == cond_id].name.values
    
################################
# reccomand therapies using CF #
################################

def my_program2(data, patient_id, cond_id):
    reccomended_ther = pd.DataFrame(columns = ['id', 'name', 'type', 'details'])

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
                ther_row['details'] = f"cured with success on itself" 
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
            patient_id_u_mat = utility_matrix_single_p(data, patient_id).to_numpy()
            # build cured patient utility matrix and calculate cosine similarity with patient id matrix
            cosine_sim = []

            for i in tqdm(pat_cured, desc="Calculating cosine distances"):
                cured_u_mat = utility_matrix_single_p(data, i).to_numpy()
                cosine_sim_pat = 1 - distance.cosine(patient_id_u_mat, cured_u_mat)
                cosine_sim.append(cosine_sim_pat)
            
            cos_sim_df = pd.DataFrame({"pat_cured" : pat_cured, 
                "cosine_similarity": cosine_sim})
            cos_sim_df_sort = cos_sim_df.sort_values("cosine_similarity", ascending=False)
            
            # extract therapies that cured the most similar patients
            for pat in cos_sim_df_sort.pat_cured.values:
                if len(reccomended_ther) < 5:
                    succ_cond_id = list(filter(lambda d: d['kind'] == cond_id, patients_df[patients_df.id == pat].conditions.values[0]))[0]['id'] 
                    ther_id = list(filter(lambda d: d['condition'] == succ_cond_id and d['successful']>90, patients_df[patients_df.id == pat].trials.values[0]))[0]['therapy']
                    
                    similarity = cos_sim_df_sort[cos_sim_df_sort.pat_cured == pat]['cosine_similarity'].values[0]
                    ther_row = therapies_df[therapies_df.id == ther_id]
                    ther_row['details'] = f"cured with success on {pat} ({similarity} cosine similarity with {patient_id})" 
                    # add only therapies that are not in the reccomandation yet
                    if ther_id not in reccomended_ther.id.values:
                        reccomended_ther = reccomended_ther.append(ther_row, ignore_index = True)

    return reccomended_ther
                
res = my_program2(data, "pat_6", "cond_2")   

count = 1
with open("../results/results.txt", 'a') as f:
        f.write(f"Output for 'funzione({patient_id}, {cond_id}' \n Recommended therapies for {patient_id} to treat condition {cond}: \n")
        for idx,row in res.iterrows():
            #with open("../../results/results.txt", 'a') as f:
            f.write(f'{count}^: {row.id}  |  {row.name}  |  {row.type}  |  {row.details} \n')
            count += 1
        f.write("-----------------------------------------------------------------------------------------------------------------------------------------\n")

#res.to_csv("../results/results.txt", index=None, sep='|', mode='a')