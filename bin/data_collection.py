import pandas as pd
import requests
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
import sys

sys.path.append('../')
from src.data_collection.utilities import cond_ther_collection, patients_collection, generate_full_patients 


# CONDITION DATA COLLECTION
cond_url = "https://www.nhsinform.scot/illnesses-and-conditions/a-to-z"

cond_dict = cond_ther_collection(cond_url, "Conditions")

# THERAPIES DATA COLLECTION
ther_url = "https://www.nhsinform.scot/tests-and-treatments/a-to-z"

ther_dict = cond_ther_collection(ther_url, "Therapies")

# PATIENTS DATA COLLECTION
patients_dict = patients_collection()

# setup
list_of_conditions_ids = [x['id'] for x in cond_dict['Conditions']]
list_of_therapies_ids = [x['id'] for x in ther_dict['Therapies']]

# and execute
full_patients_dict = generate_full_patients(patients_dict, list_of_conditions_ids, list_of_therapies_ids)
print(full_patients_dict)

# bind the dictionaries
final_data_dict = cond_dict | ther_dict | full_patients_dict

# save it as .json
with open('../data/full_data.json', 'w') as fp:
    json.dump(final_data_dict, fp, indent=4, default=str)
print("> JSON stored correctly")