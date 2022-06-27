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
patients_dict = patients_collection(5000, 5000)

print("Generate patients conditions and trials")
list_of_conditions_ids = [x['id'] for x in cond_dict['Conditions']]
list_of_therapies_ids = [x['id'] for x in ther_dict['Therapies']]

full_patients_dict = generate_full_patients(patients_dict, list_of_conditions_ids, list_of_therapies_ids)

#####################
# CREATE FINAL DATA #
#####################
print("Merge data and produce the final dataset")
# bind the dictionaries
final_data_dict = cond_dict | ther_dict | full_patients_dict

# save it as .json
with open('../data/full_data.json', 'w') as fp:
    json.dump(final_data_dict, fp, indent=4, default=str)
print("> JSON stored correctly")