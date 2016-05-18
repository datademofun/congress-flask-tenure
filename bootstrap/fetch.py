"""
Just a script to pull data and fill datafoo/cache
with JSON files

Run from the top-level directory:

$ python scripts/build_cache.py

And datafoo/cache will magically populate
"""


from os.path import join, basename, splitext
import json
import requests
import yaml
FETCHED_DIR = join('bootstrap', 'fetched')
SOURCE_PATH = 'https://raw.githubusercontent.com/unitedstates/congress-legislators/master/'
SOURCE_FILES = ['committees-current.yaml', 'legislators-current.yaml',
                'legislators-social-media.yaml', 'committee-membership-current.yaml']



def fetch_data():
    for sf in SOURCE_FILES:
        url = SOURCE_PATH + sf
        bname, _ex = splitext(basename(url))
        fname = join(FETCHED_DIR, '{name}.json'.format(name=bname))

        txt = requests.get(url).text
        data = yaml.load(txt) # deserialize the data

        with open(fname, 'w') as wf:
            print("Saving to", fname)
            jtxt = json.dumps(data, indent=2)
            wf.write(jtxt)
            # and then reserialize it as JSON


if __name__ == '__main__':
    fetch_data()
