from userauth.models import CustomUser as User, Year
#for user in users:
#    if 'Parkin' in user.last_name:
#        print('%s %s (%s)'%(user.last_name, user.first_name, user.id))
#        u = user
u = User.objects.get(id=1278)
entries = u.entry_set.all()
