
# Run this using 
# 
#   ./manage.py shell < update_raw_status.py
#
#

# This has been edited to import from a csv rather than just splitting 

from userauth.models import CustomUser as User, Year
from entries.models import Entry
import pandas as pd


df = pd.read_csv('nlpa_second_round_entries-FIXED.csv')
l = len(df)
entries = []
for i in range(l):
    row = df.loc[i]
    email = row['email']
    id = row['id']
    entry_id = row['entry_id']
    entries.append( {'email': email, 'entry_id': int(entry_id), 'id': int(id)} )

for entry in entries:
    e = Entry.objects.get(id=entry['entry_id'])
    e.in_second_round = True
    e.save()
