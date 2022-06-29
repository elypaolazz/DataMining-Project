# libraries
import pandas as pd
import random
import datetime
import requests
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
from names_dataset import NameDataset
from multiprocessing import Process
import itertools


#######################
# utilities functions #
#######################
def generate_random_date(min_date=None, type="condition"):
    """
    Generate and returns a random date between 1/1/2010 and 1/1/2020 (as datetime.date)
    """

    # setup start and end date
    start_date = datetime.date(2000, 1, 1)

    if type == "condition":
        end_date = datetime.date(2010, 1, 1)
    elif type == "trial":
        end_date = datetime.date(2020, 1, 1)
    else:
        raise Exception(f"ERROR: type '{type}' not available")

    # update min date, if not None
    if min_date is not None:
        start_date = min_date

    # obtain random date
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)

    # return random date
    return random_date

def get_random_id(list_of_ids):
    """
    Get the id of a condition/therapy (str)
    """
    return random.sample(list_of_ids,1)[0]


#################################
# COND & THER generate function #
#################################
def cond_ther_collection(page_url, topic):
    """
    Collect data about conditions and therapies from NHS web pages and generate dictionaries
    """
    header = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'}
    r = requests.get(page_url,headers=header)

    # check the response code (it should be 200)
    print(f"> Status Code: {r.status_code}")

    # and obtain the content
    soup_cond = BeautifulSoup(r.text, 'lxml')
    print(f'> {topic} web page obtained')

    # the info is stored in the 'a' tags, with class 'nhs-uk__az-link'
    links = soup_cond.find_all('a',attrs={"class":"nhs-uk__az-link"})

    # setup placeholders and variables
    BASE_LINK_C = 'https://www.nhsinform.scot/' # useful to complete the href link
    name_list = []
    href_list = []

    # iterate over obtained tags
    for link in links:

        # preprocess name
        clean_name = link.text.replace('\r','').replace('\n','').replace('\t','')
        
        # save it in the list
        name_list.append(clean_name)

        # obtain href link (for the type page)
        href_list.append(BASE_LINK_C + link.get('href'))

    # obtain info about type
    # initialize placeholder
    types_list = []
    
    # keep track of errors
    errors_str = "> There were some errors in the retrieving of the data:\n"

    # iterate over conditions pages links
    for link in tqdm(href_list, desc="> Scraping Web Pages"):
        
        # connect
        r = requests.get(link,headers=header)

        # check for status code
        if r.status_code == 200:

            try:
                # obtain content 
                soup = BeautifulSoup(r.text, 'lxml')

                # obtain 'a' with class 'nhsuk-breadcrumb__link'
                links = soup.find_all('a',attrs={"class":"nhsuk-breadcrumb__link"})

                # save it in the list
                types_list.append(links[2].text)

            except Exception as e:
                types_list.append("ERROR")                
                errors_str += f"   * Error while retrieving page '{link}' [{str(e)}]\n"


        # if the page could not be reached, print a warning
        else:
            types_list.append("ERROR")
            errors_str += f"   * Error while retrieving page '{link}' [status code was '{r.status_code}' instead of 200]\n"

    # show errors
    print(errors_str)
    
    # aggragate data
    # create the df from lists
    temp_df = pd.DataFrame(
        data=zip(name_list, types_list),
        columns=["name","type"]
    )

    # remove error types
    temp_df = temp_df.loc[temp_df["type"] != "ERROR"].reset_index()

    if topic == "Conditions":
        # add column with conditions ids
        ids = [f"cond_{n}" for n in range(len(temp_df))]
        temp_df["id"] = ids
    else:
        # add column with conditions ids
        ids = [f"ther_{n}" for n in range(len(temp_df))]
        temp_df["id"] = ids

    # reorder columns
    temp_df = temp_df[["id", "name", "type"]]
    
    # create dict
    if topic == "Conditions":
        RESULT_DICT = {"Conditions":[]}
        for idx,row in temp_df.iterrows():
            RESULT_DICT["Conditions"].append(
                {
                    "id":row["id"],
                    "name":row["name"],
                    "type":row["type"],
                }
        )
    else:
        RESULT_DICT = {"Therapies":[]}
        for idx,row in temp_df.iterrows():
            RESULT_DICT["Therapies"].append(
                {
                    "id":row["id"],
                    "name":row["name"],
                    "type":row["type"],
                }
        )
            
    return RESULT_DICT
            
####################################
# PATIENTS names generate function #
####################################         
def patients_collection(n_of_female, n_of_male):
    """
    Collect data about people's name from NameDataset and generate a dictionary
    """
    # import data
    print(f"> Loading Name dataset")
    nd = NameDataset()
    print(f"> Select most popular italian/english names")
    # female names
    fem_names_IT = nd.get_top_names(n=int(n_of_female/2), gender='Female', country_alpha2='IT')['IT']['F']
    fem_names_GB = nd.get_top_names(n=int(n_of_female/2), gender='Female', country_alpha2='GB')['GB']['F']
    list_name_F = fem_names_IT + fem_names_GB
    # male names
    male_names_IT = nd.get_top_names(n=int(n_of_male/2), gender='Male', country_alpha2='IT')['IT']['M']
    male_names_GB = nd.get_top_names(n=int(n_of_male/2), gender='Male', country_alpha2='GB')['GB']['M']
    list_name_M = male_names_IT + male_names_GB
    # female placeholder
    gender_F = ["Female"]*len(list_name_F)
    # male placeholder
    gender_M = ["Male"]*len(list_name_M)

    # bind name and gender lists
    names = list_name_F + list_name_M
    gender = gender_F + gender_M

    # create ages vector
    ages = []
    for n in range(0,10000):
        age = random.sample(range(18,99), 1)[0]
        ages.append(age)
    
    # create df
    patients_df = pd.DataFrame(
        data=zip(names, gender, ages),
        columns=["patient_name","patient_gender","patient_age"]
    )
    patients_df

    # sort data
    patients_df = patients_df.sort_values("patient_name").reset_index(drop=True)

    # add column with conditions ids
    patients_ids = [f"pat_{n}" for n in range(len(patients_df))]
    patients_df["patient_id"] = patients_ids

    # reorder columns
    patients_df = patients_df[["patient_id", "patient_name", "patient_gender","patient_age"]]

    # create the dict
    RESULT_DICT = {"Patients":[]}
    for idx,row in patients_df.iterrows():
        RESULT_DICT["Patients"].append(
            {
                "id":row["patient_id"],
                "name":row["patient_name"],
                "gender":row["patient_gender"],
                "age":row["patient_age"],
                "conditions": [],
                "trials": [],
            }
        )
    return RESULT_DICT

#######################################################
# PATIENTS conditions and therapies generate function #
#######################################################
def generate_full_patients(patients_dict, list_of_conditions_ids, list_of_therapies_ids, max_n_cond, max_n_ther):
    """
    Generate conditions and therapies for each patients and fill the patients dictionary
    """
    # generate conditions and trials for patients
    for patient_dict in patients_dict['Patients']:
      
        # print(f"> PATIENT '{patient_dict['name']}' [ID: {patient_dict['id']}]")
      
        # CONDITIONS

        # obtain the number of conditions to generate
        NUM_OF_CONDITIONS = random.sample(range(1,max_n_cond), 1)[0]
        # print(f'  * Number of conditions: {NUM_OF_CONDITIONS}')

        # get a copy of all the possible conditions
        list_of_conditions_ids_copy = list_of_conditions_ids.copy()

        # create N conditions
        for idx in range(NUM_OF_CONDITIONS):

            # create condition dictionary
            temp_condition = {}

            # set 'id' 
            temp_condition['id'] = f'c{idx+1}'

            # generate a random date

            # if conditions are already present for the patient --> get the last date
            if len(patient_dict['conditions']) > 0:
                last_date = patient_dict['conditions'][-1]['diagnosed']
            else:
                last_date = None

            # generate the date
            temp_condition['diagnosed'] = generate_random_date(min_date=last_date, type="condition")

            # set 'cured' to None
            temp_condition['cured'] = None

            # set 'kind' to a random condition id
            temp_cond_id = get_random_id(list_of_conditions_ids_copy)
            temp_condition['kind'] = temp_cond_id
            list_of_conditions_ids_copy.remove(temp_cond_id) # ensure that there are no duplicates conditions

            # add the condition dictionary to the patient
            patient_dict['conditions'].append(temp_condition)

      # TRIALS
      
        for condition in patient_dict['conditions']:

            # setup
            CREATE_NEW_TRIALS = True

            # obtain the number of therapies to generate
            NUM_OF_TRIALS = random.sample(range(0,max_n_ther), 1)[0]
            # print(f"  * Number of trials for condition '{condition['id']}': {NUM_OF_TRIALS}")

            # get a copy of all the possible therapies
            list_of_therapies_ids_copy = list_of_therapies_ids.copy()

            temp_min_date = condition['diagnosed']
            for idx in range(NUM_OF_TRIALS):
                if CREATE_NEW_TRIALS:

                    # create trial dictionary
                    temp_trial = {}

                    # set 'id' 
                    temp_trial['id'] = condition['id'] + f'_t{idx+1}'

                    # set 'start'
                    temp_trial['start'] = generate_random_date(min_date=temp_min_date, type="trial")

                    # set 'end' 
                    temp_trial_end = generate_random_date(min_date=temp_trial['start'], type="trial")
                    temp_trial['end'] = temp_trial_end
                    temp_min_date = temp_trial_end

                    # set 'condition'
                    temp_trial['condition'] = condition['id']

                    # set 'therapy'
                    temp_ther_id = get_random_id(list_of_therapies_ids_copy)
                    temp_trial['therapy'] = temp_ther_id
                    list_of_therapies_ids_copy.remove(temp_ther_id) # ensure that there are no duplicates therapies

                    # set 'successful'
                    SUCC = random.sample(range(0,100), 1)[0]
                    temp_trial['successful'] = SUCC

                    if SUCC > 90:
                        condition['cured'] = temp_trial['end']
                        CREATE_NEW_TRIALS = False

                    # add the trial dictionary to the patient
                    patient_dict['trials'].append(temp_trial)

      # print("-"*100)
   
    return patients_dict

################################################
# reccomandation algorithm utilities functions #
################################################

def utility_matrix(patient_id):
    # open dataset
    with open('../../data/full_data.json', 'r') as file:
        data = json.load(file)
    
    conditions_df = pd.DataFrame(data['Conditions'])
    therapies_df = pd.DataFrame(data['Therapies'])
    patients_df = pd.DataFrame(data['Patients'])
    
    # initialize empty utility matrix
    prova = pd.DataFrame(columns = list(therapies_df['id'].values), index= list(conditions_df['id'].values))
    
    # extract data for the patient
    pat = patients_df[patients_df.id == patient_id]

    # trials and cond
    trials = pd.DataFrame(pat.trials.values[0])
    cond = pd.DataFrame(pat.conditions.values[0])
    
    # add true cond_id to trial data
    trials['cond_id'] = ""

    for idx,row in trials.iterrows():
        pat_cond = row['condition']
        cond_id = cond[cond.id == pat_cond].kind.values[0]
        trials.loc[idx,'cond_id'] = cond_id
        
    # fill utility matrix
    for idx,row in trials.iterrows():
        matrix_pat = prova
        
        cond = row['cond_id']
        ther = row['therapy']
        succ = row['successful']
        matrix_pat.loc[cond,ther] = succ
    # normalize
    # norm_matrix = matrix_pat.sub(matrix_pat.mean(axis=1), axis=0)
    # final_matrix = norm_matrix.fillna(0)
    final_matrix = matrix_pat.fillna(0)
    return final_matrix

def utility_matrix_single_p(data, patients_id):
    # # open dataset
    # with open('../../data/full_data.json', 'r') as file:
    #     data = json.load(file)
    
    conditions_df = pd.DataFrame(data['Conditions'])
    therapies_df = pd.DataFrame(data['Therapies'])
    patients_df = pd.DataFrame(data['Patients'])
    
    # initialize empty utility matrix
    c = list(itertools.product(conditions_df.id.values, therapies_df.id.values))
    prova = pd.DataFrame(columns = c, index= list([patients_id]))
    
    # extract data for the patient
    pat = patients_df[patients_df.id == patients_id]

    # trials and cond
    trials = pd.DataFrame(pat.trials.values[0])
    cond = pd.DataFrame(pat.conditions.values[0])
    
    # add true cond_id to trial data
    trials['cond_id'] = ""

    for idx,row in trials.iterrows():
        pat_cond = row['condition']
        cond_id = cond[cond.id == pat_cond].kind.values[0]
        trials.loc[idx,'cond_id'] = cond_id
        
    # fill utility matrix
    for idx,row in trials.iterrows():
        matrix_pat = prova
        
        cond = row['cond_id']
        ther = row['therapy']
        succ = row['successful']
        col = (cond, ther)
        matrix_pat.at[patients_id, col] = succ
    # normalize
    # norm_matrix = matrix_pat.sub(matrix_pat.mean(axis=1), axis=0)
    # final_matrix = norm_matrix.fillna(0)
    final_matrix = matrix_pat.fillna(0)
    return final_matrix
 
   