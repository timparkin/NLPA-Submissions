import pandas as pd
import requests
import os
import math
from pathlib import Path
import sys

# This is the code that gets the images from the data storage which should be the server in this case
# We need a source csv, a sample of which is in this folder

# get the target folder
base=sys.argv[1]
# get the source csv file e.g. '~/nlpa_combined_entries-final-cleaned-extra.csv'
source_csv = sys.argv[2]

def save_photo_from_url(url, filename, category, directory, id):
    print('%s : %s %s'%(id, filename, directory))
    target_directory = os.path.join(base, category, directory)
    Path(target_directory).mkdir(parents=True, exist_ok=True)
    target_filename =  os.path.join(target_directory, filename)
    if not os.path.isfile(target_filename):
        with open(target_filename, 'wb') as handle:
            response = requests.get(url, stream=True)

            if not response.ok:
                print(response)

            for block in response.iter_content(1024):
                if not block:
                    break

                handle.write(block)

df = pd.read_csv(source_csv)

space = 0
for i in range(len(df)):
#for i in range(100):
    row = df.loc[i]
    url = 'https://submit.naturallandscapeawards.com/%s'%row['entry_url']

    id = row['entry_id']
    if not isinstance(url,str):
        continue
    filename = str(row['entry_filename'])
    if 'entries' in filename:
        filename = filename.split('/')[-1]
    name = row['name']
    size = row['entry_photo_size']
    category = row['entry_category']
    if not isinstance(category, str):
        category = 'undefined'

    if not math.isnan(size):
        space += size
        save_photo_from_url(url, filename, category, name, id)
        print('{:=4.1f}Mb'.format(int(size/100000)/10))

print('{:=4.1f}Mb'.format(int(space/100000000)/10))
