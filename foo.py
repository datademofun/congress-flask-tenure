import json
from os.path import join
DATA_DIR = join('.', 'static', 'data')
LEGISLATORS_FILENAME = join(DATA_DIR, 'legislators.json')
COMMITTEES_FILENAME = join(DATA_DIR, 'committees.json')

def get_legislators():
    with open(LEGISLATORS_FILENAME) as rf:
        data = json.load(rf)
    return data

def get_committees():
    with open(COMMITTEES_FILENAME) as rf:
        data = json.load(rf)
    return data


def print_record_count():
    print("Legislators:", len(get_legislators()))
    print("Committees:", len(get_committees()))
