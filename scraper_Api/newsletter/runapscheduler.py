from django_apscheduler.jobstores import DjangoJobStore, register_events
from apscheduler.schedulers.background import BackgroundScheduler
from .task import test
import sys

from django_apscheduler.models import DjangoJob

DjangoJob.objects.all().delete()

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


def start():
    try:
        scheduler = BackgroundScheduler()
        scheduler.add_jobstore(DjangoJobStore(), "default")
        scheduler.add_job(test, 'interval',
                          name="server_sends_emails", seconds=10, jobstore='default')
        register_events(scheduler)
        scheduler.start()

        print("Scheduler started...", file=sys.stdout)
    except Exception:
        print("something wrong")
