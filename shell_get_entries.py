from userauth.models import CustomUser as User, Year
from entry.models import Entry

e = Entry.objects.get(id=20)
e.in_second_round = True
e.save()
