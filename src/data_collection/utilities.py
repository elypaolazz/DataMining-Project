# libraries
import pandas as pd
import random
import datetime

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