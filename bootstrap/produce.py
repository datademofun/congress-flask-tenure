import fetch
import wrangle
from os.path import join
from os import makedirs
from shutil import copyfile
DEST_DIR = join('static', 'data')
makedirs(DEST_DIR, exist_ok=True)

if __name__ == '__main__':
    print("Fetching data")
    fetch.fetch_data()

    print("Wrangling data")
    wrangle.wrangle_legislators()
    wrangle.wrangle_committees()

    print("Pushing data to static/data")
    # push the wrangled legislators
    src_fname = wrangle.DEST_LEGISLATORS_FILENAME
    dest_fname = join(DEST_DIR, 'legislators.json')
    print("Saving", src_fname, 'to', dest_fname)
    copyfile(src_fname, dest_fname)


    src_fname = wrangle.DEST_COMMITTEES_FILENAME
    dest_fname = join(DEST_DIR, 'committees.json')
    print("Saving", src_fname, 'to', dest_fname)
    copyfile(src_fname, dest_fname)
