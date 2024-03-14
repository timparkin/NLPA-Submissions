from userauth.models import CustomUser as User, Year
from entry.models import Entry

entries = []
with open('finals_export_ids_2023.csv') as file:
    lines = file.readlines()
    for line in lines:
        email,id,entry_id = line.split(',')
        entries.append( {'email': email, 'entry_id': int(entry_id), 'id': int(id)} ) 
print(entries)
#for entry in entries:
#    e = Entry.objects.get(id=entry['entry_id'])
#    e.in_second_round = True
#    e.save()
