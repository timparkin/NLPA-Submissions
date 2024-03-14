
from django.core.management.base import BaseCommand
from userauth.models import CustomUser as User, Year
from entries.models import Entry

from nlpa.settings.config import CURRENT_YEAR


entries = []

class Command(BaseCommand):
    def handle(self, **options):
        with open('finals_export_ids_2023.csv') as file:
            lines = file.readlines()
            for line in lines:
                email,id,entry_id = line.split(',')
                entries.append( {'email': email, 'entry_id': int(entry_id), 'id': int(id)} ) 
        for entry in entries:
            e = Entry.objects.get(id=entry['entry_id'])
            e.in_second_round = True
            e.save()
        self.stdout.write(self.style.SUCCESS('Successfully updated "%s" entries' % len(entries)))
