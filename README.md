# DataMining-Project 2021/2022
## Therapies collaborative filtering recommendation systems engine

## Prerequisites 

In order to execute the project's code, a version of Python 3, preferably [3.9](https://www.python.org/downloads/release/python-390/), has to be installed.

Besides that, the scripts employs the following libraries, which need to be installed as well:
- `bs4 0.0.1`
- `names-dataset 3.1.0`
- `numpy 1.22.4`
- `pandas 1.4.2`
- `requests 2.28.0`
- `scikit-learn 1.1.1`
- `scipy 1.8.1`
- `sklearn 0.0`
- `tqdm 4.64.0`
- `urllib3 1.26.9`

For a quick installation of libraries, you can run:
```
pip install requirements.txt
```
It is recommended to create a virtual environment for the project, where to install the required libraries. 

## Data generation script

The data have already been generated and stored in the `data` folder, however, you can reproduce the data collection process choosing the number of patients to include in the dataset, their maximum number of condition and the maximum number of trials for each condition. This can be done moving to the `bin directory` and running:

```
python data_collection.py <n_patients> <max_n_cond_x_patient> <max_n_trial_x_cond>
```
The new generated dataset will be stored in the `data` folder.

## Therapies recommendation systems execution

The recommendation systems algorithm can be executed by specifying the dataset path, a patient ID and a condition ID. Note that both patient and condition have to be present in the dataset.
Hence, you can run:
```
python myprogram.py <dataset_path> <patient_id> <cond_id>
```
The algorithm applies a collaborative filtering approach to recommend a therapy with a high estimate of success for the chosen patient and condition. In particular, the output will be an ordered list of the top 5 therapies recommended to the patient to treat the condition. This will be stored in the `results.txt` file in the `results` folder.

## Other scripts

The `src` contains some other useful scripts:
- `utilities.py`, where most of the utility functions used in the recommendation and data collection scripts are defined;
- `test.ipynb`, the Python notebook used to produce the 15 required tests (he results of the tests are stored in `results/test.txt`);
- `baseline_method.py`, the script used for the baseline method based evaluation.

The baseline method evaluation was conducted by comparing the performance of the best model (the algorithm employed for the final recommendation engine) and a collaborative filtering baseline model. The latter uses more naïve computation for the utility matrix construction and cosine similarity. 
You can re-perform the baseline evaluation moving to the `src` folder and running:
```
python baseline_method <dataset_path> <patient_id> <cond_id>
```
An then running:
```
python myprogram.py <dataset_path> <patient_id> <cond_id> baseline_evaluation
```

The result of the two runs with the corresponding performances are stored in the file `results/baseline_eval.txt`.

### Overall code structure
```
├── bin
│   ├── data_collection.py
│   └── myprogram.py
│
├── data
│   └── full_data.json
│ 
├── doc
│   └── report.pdf
│ 
├── results
│    ├── results.txt
│    └── test.txt
├── src
│    ├── test.ipynb
│    ├── utilities.py
│    └── 
|
├── requirements.txt
└── README.md
```