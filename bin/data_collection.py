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
# import useful functions
sys.path.append('../')
from src.utilities import cond_ther_collection, patients_collection, generate_full_patients 

#####################
# parameter setting #
#####################

# all the arguments must be passed, the order IS relevant
if len(sys.argv) == 5: # NB: 4 because argv[0] is the name of the script
    # dataset path
    data_path = str(sys.argv[1])
    # number of patients
    n_patients = int(sys.argv[2])
    # maximum number of conditions per patients
    n_cond_x_pat = int(sys.argv[3])
    # maximum number of therapies for each condition
    n_ther_x_pat = int(sys.argv[4])
    print("> Parameters setted")
else:
    # Default parameters if nothing is passed
    data_path = '../data/full_data.json'
    n_patients = 10000
    n_cond_x_pat = 20
    n_ther_x_pat = 12

#############################
# CONDITION DATA COLLECTION #
#############################
print("Collecting Conditions")
cond_url = "https://www.nhsinform.scot/illnesses-and-conditions/a-to-z"

cond_dict = cond_ther_collection(cond_url, "Conditions")

#############################
# THERAPIES DATA COLLECTION #
#############################
print("Collecting Therapies")
ther_url = "https://www.nhsinform.scot/tests-and-treatments/a-to-z"

ther_dict = cond_ther_collection(ther_url, "Therapies")

############################
# PATIENTS DATA COLLECTION #
############################
print("Collecting Patients names")
patients_dict = patients_collection(n_patients/2, n_patients/2)

print("Generate patients conditions and trials")
list_of_conditions_ids = [x['id'] for x in cond_dict['Conditions']]
list_of_therapies_ids = [x['id'] for x in ther_dict['Therapies']]

full_patients_dict = generate_full_patients(patients_dict, list_of_conditions_ids, list_of_therapies_ids, n_cond_x_pat, n_ther_x_pat)

#####################
# CREATE FINAL DATA #
#####################
print("Merge data and produce the final dataset")
# bind the dictionaries
final_data_dict = cond_dict | ther_dict | full_patients_dict

# save it as .json
with open(data_path, 'w') as fp:
    json.dump(final_data_dict, fp, indent=4, default=str)
print("> JSON stored correctly")