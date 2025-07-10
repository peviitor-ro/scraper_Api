from django.core.management.base import BaseCommand
from company.runapscheduler import start

import time

class Command(BaseCommand):
    help = 'Pornește APScheduler-ul pentru ștergerea companiilor inactive.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Pornesc schedulerul..."))
        start()

        # Ținem procesul activ
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Scheduler oprit manual."))
