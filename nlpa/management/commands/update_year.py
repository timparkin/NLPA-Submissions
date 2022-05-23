from django.core.management.base import BaseCommand
from userauth.models import CustomUser as User, Year

from nlpa.settings.config import CURRENT_YEAR

class Command(BaseCommand):
    def handle(self, **options):
        count = 0
        users = User.objects.all()
        for user in users:
            years = Year.objects.filter(user=user, year=CURRENT_YEAR-1)
            if not years:
                year = Year.objects.create(user=user, year=CURRENT_YEAR-1)
                year.payment_status = user.payment_status
                year.payment_plan = user.payment_plan
                year.payment_upgrade_status = user.payment_upgrade_status
                year.payment_upgrade_plan = user.payment_upgrade_plan
                year.is_young_entrant = user.is_young_entrant
                year.project_title_one = user.project_title_one
                year.project_description_one = user.project_description_one
                year.project_title_two = user.project_title_two
                year.project_description_two = user.project_description_two
                year.save()
                count += 1
            user.payment_status = None
            user.payment_plan = None
            user.payment_upgrade_status = None
            user.payment_upgrade_status = None
            user.is_young_entrant = False
            user.project_title_one = None
            user.project_description_one = None
            user.project_title_two = None
            user.project_description_two = None
            user.save()

            entries = user.entry_set.all()
            for entry in entries:
                if entry.year is None:
                    entry.year = CURRENT_YEAR-1
                    entry.save()
        self.stdout.write(self.style.SUCCESS('Successfully updated "%s" users' % count))
