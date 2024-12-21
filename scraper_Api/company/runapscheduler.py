from django_apscheduler.jobstores import DjangoJobStore, register_events
from apscheduler.schedulers.background import BackgroundScheduler
import sys
from .models import Company, DataSet
from datetime import datetime

from django_apscheduler.models import DjangoJob

DjangoJob.objects.all().delete()

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "clean")


def clean():
    today = datetime.now().date()

    companies = Company.objects.all()
    for company in companies:
        data = DataSet.objects.filter(company=company).first()

        if data is None or (today - data.date).days > 3:
              print(f"Deleting {company.company}")
              company.delete()


def start():
    try:
        scheduler = BackgroundScheduler()
        scheduler.add_jobstore(DjangoJobStore(), "clean")
        scheduler.add_job(clean, 'interval', days=3, jobstore='clean')
        register_events(scheduler)
        scheduler.start()

        print("Scheduler started...", file=sys.stdout)
    except Exception:
        print("something wrong")
