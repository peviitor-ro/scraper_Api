from django.db import connection
import sys
from django_apscheduler.models import DjangoJob
from datetime import datetime
from .models import Company, DataSet
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.core.paginator import Paginator


# Șterge toate joburile existente din baza de date pentru a evita duplicările
DjangoJob.objects.all().delete()

def clean():
    """Șterge companiile fără date recente, lot cu lot."""
    today = datetime.now().date()
    
    try:
        companies = Company.objects.all().order_by('id')
        paginator = Paginator(companies, 100)  
        for page_number in paginator.page_range:
            page = paginator.page(page_number)
            for company in page.object_list:
                last_data = DataSet.objects.filter(company=company).last()
                if not last_data or (today - last_data.date).days >= 2:
                    company.delete()
                    print(f"Deleted company: {company.company}", file=sys.stdout)
    finally:
        connection.close() 


def start():
    """ Pornește APScheduler cu jobul `clean` care rulează la fiecare 12 ore. """
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    if scheduler.running:
        print("Scheduler already running.", file=sys.stdout)
        return

    try:
        scheduler.add_job(clean, 'interval', days=1, jobstore='default', id='clean_job', replace_existing=True)

        register_events(scheduler)
        scheduler.start()
        print("Scheduler started successfully!", file=sys.stdout)
    except Exception as e:
        print(f"Error starting scheduler: {e}", file=sys.stderr)
