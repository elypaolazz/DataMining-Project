# Therapies collaborative filtering recommendation engine
## DataMining-Project 2021/2022

### Project desription
The aim of the project is to provide a solution capable of solving the problem of recommending the most suitable therapies to a patient suffering from a disease. The solution proposed in this paper involves the implementation of a collaborative filtering recommendation system and the construction of a test dataset containing medical data. In this data we find fundamental entities:
conditions, all possible diseases;
therapies, all possible treatments;
patients, individuals characterised by a medical history.
The patient's medical history is represented by the set of conditions he/she has experienced and the set of therapies (called trials) he/she has tested to treat them.
This proposed system attempts to predict the patient's response to a given therapy based on the similarity of his/her medical history with that of other patients. Moreover, the system is able to recommend top-5 therapies on the basis of these predictions. 

### Prerequisites 

In order to execute the project's code, a version of Python 3, preferably [3.9](https://www.python.org/downloads/release/python-390/), has to be installed.

Besides that, the scripts employs the following libraries, which need to be installed as well:
- `bs4 0.0.1`
- `names-dataset 3.1.0`
- `numpy 1.22.4`
- `pandas 1.4.2`
- `requests 2.28.0`
- `scikit-learn 1.1.1`
- `scipy 1.8.1`
- `tqdm 4.64.0`
- `urllib3 1.26.9`

For a quick installation of libraries, you can run in your command line:
```
pip install requirements.txt
```
It is recommended to create a virtual environment where to install the required libraries. 

### Data generation script

The data have already been generated and stored in the `data` folder, however, you can reproduce the data collection process choosing the number of patients to include in the dataset, their maximum number of condition and the maximum number of trials for each condition. This can be done moving to the `bin` directory and running:

```
python data_collection.py <data_path> <n_patients> <max_n_cond_x_patient> <max_n_trial_x_cond>
```
The new generated dataset will be stored in the in the chosen path ('<data path>').

### Therapies recommendation systems execution

The `bin` folder contains contains the executable scripts of the solution.
The recommendation systems algorithm can be executed by specifying the dataset path, a patient ID and a condition ID. Note that both patient and condition have to be present in the dataset.
Hence, you can run:
```
python ther_recommendation.py <dataset_path> <patient_id> <cond_id> single_run
```
The algorithm applies a collaborative filtering approach to recommend a therapy with a high estimate of success for the chosen patient and condition. In particular, the output will be an ordered list of the top 5 therapies recommended to the patient to treat the condition. This will be stored in the `results.txt` file.

### Other scripts

The `src` folder contains some other useful scripts:
- `utilities.py`, where most of the utility functions used in the recommendation and data collection scripts are defined;
- the `data_collection` folder, which contains notebooks explaining in detail the data collection and generation;
- `test.ipynb`, the Python notebook used to produce the 15 required test cases (the results of the tests are stored in `results/test.txt`);
- `baseline_method.py`, containing the baseline method algorithm.

#### Baseline evaluation
The baseline method evaluation was conducted by comparing the performance of the best model (the algorithm employed for the final recommendation engine) and a collaborative filtering baseline model. The latter uses more naïve computation for the utility matrix construction and cosine similarity. 
You can re-perform the baseline evaluation moving to the `src` folder and running:
```
python baseline_method <dataset_path> <patient_id> <cond_id>
```
An then running:
```
python ther_recommendation.py <dataset_path> <patient_id> <cond_id> baseline_evaluation
```
The result of the two runs with the corresponding time execution performances are stored in the file `results/baseline_eval.txt`.

### Overall code structure
The `doc` folder contains the project report
```
├── bin
│   ├── data_collection.py
│   ├── ther_recommendation.py
│   └── results.txt
│
├── data
│   └── full_data.json
│ 
├── doc
│   └── DM_project_report.pdf
│ 
├── results
│    ├── results.txt
│    ├── scalability_test.ipynb
│    └── test.txt
├── src
│    ├── test.ipynb
│    ├── utilities.py
│    └── data_collection
|       ├── 1.cond_ther_collection.ipynb
│       ├── 2.patients_collection.ipynb
|       ├── 3.final_data_creation.ipynb
│       └── intermediate data
|           ├── cond_ther.json
│           └── patients.json
|
├── requirements.txt
└── README.md
```

A brief description of each folder follows:
- `bin`, contains the files of the program execution along with the results it produces through the various executions performed;
- `data`, contains the generated dataset which includes 10000 patients with a maximum of 20 conditions each and a maximum of 12 trials for each conditions;
- `doc`, which contains the project report;
- `results`, containing the results of the various tests ( for the 15 required test cases, baseline and scalability evaluation);
- `src`, which contains all the useful scripts for running the program and conducting the tests.
