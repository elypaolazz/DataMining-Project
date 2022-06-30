import sys
sys.path.append('../')
import bin.reccomandation
import os
import random
import pandas as pd
import json
import subprocess
from bs4 import BeautifulSoup


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

# choice randomly 15 patients and their coditions
list_pat = random.choices(patients_df.id.values, k=15)
list_cond = random.choices(conditions_df.id.values, k=15)
test_df = pd.DataFrame({"patient": list_pat, "condition": list_cond})

# for idx,row in test_df.iterrows():
#     execution = f"reccomandation.py ../data/full_data.json {row.patient} {row.condition}"
#     os.system(execution)

# os.system('reccomandation.py ../data/full_data.json pat_0 cond_0')


subprocess.run(['../bin/reccomandation.py', '../data/full_data.jso', 'pat_1', 'cond_1'])