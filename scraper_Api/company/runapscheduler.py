from django_apscheduler.jobstores import DjangoJobStore, register_events
from apscheduler.schedulers.background import BackgroundScheduler
from .models import Company, DataSet
from datetime import datetime
from django.db import connection
from django_apscheduler.models import DjangoJob
import sys

# Șterge toate joburile existente din baza de date pentru a evita duplicările
DjangoJob.objects.all().delete()

# Inițializează un singur obiect de scheduler global
scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "clean")


def clean():
    """ Șterge companiile care nu au date recente (ultimele 2 zile). """
    today = datetime.now().date()

    # Verifică și reînnoiește conexiunea la baza de date
    if connection.connection and not connection.is_usable():
        connection.close()

    for company in Company.objects.all():
        last_data = DataSet.objects.filter(company=company).last()
        if not last_data or (today - last_data.date).days >= 2:
            company.delete()


def start():
    """ Pornește APScheduler cu jobul `clean` care rulează la fiecare 12 ore. """
    global scheduler
    if scheduler.running:
        print("Scheduler already running.", file=sys.stdout)
        return

    try:
        scheduler.add_job(clean, 'interval', days=1, jobstore='clean')
        register_events(scheduler)
        scheduler.start()
        print("Scheduler started successfully!", file=sys.stdout)
    except Exception as e:
        print(f"Error starting scheduler: {e}", file=sys.stderr)