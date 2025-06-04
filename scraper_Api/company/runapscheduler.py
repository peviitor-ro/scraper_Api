import logging
import atexit
from django.db import connection
from django_apscheduler.models import DjangoJob
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.core.paginator import Paginator
from .models import Company, DataSet
from jobs.models import Job


DjangoJob.objects.all().delete()

# Configurare logging pentru debugging
logging.basicConfig(level=logging.DEBUG)

# Inițializare globală APScheduler
scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


def unpublish_jobs(company):
    jobs = Job.objects.filter(company=company)
    for job in jobs:
        if job.published:
            job.unpublish()


def clean():
    """Șterge companiile fără date recente, lot cu lot."""
    logging.info("Job clean() a început!")
    today = datetime.now().date()

    try:
        batch_size = 100
        last_id = 0
        while True:
            companies = Company.objects.filter(
                id__gt=last_id).order_by('id')[:batch_size]
            if not companies:
                break

            for company in companies:
                last_id = company.id
                last_data = DataSet.objects.filter(company=company).last()
                if not last_data or (today - last_data.date).days >= 2:
                    if company.source:
                        company.delete()
                        logging.info(
                            f"Compania {company.company} a fost ștearsă.")
                    else:
                        unpublish_jobs(company)
                        logging.info(
                            f"Joburile pentru compania {company.company} au fost dezpublicate.")
        logging.info("Jobul clean() s-a încheiat cu succes!")

    except Exception as e:
        logging.error(f"Eroare în funcția clean: {e}")
    finally:
        connection.close()  # Închide conexiunea MySQL pentru a evita "Broken pipe"


def start():
    """Pornește APScheduler doar dacă nu rulează deja."""
    global scheduler

    if not DjangoJob.objects.filter(id="clean_job").exists():
        logging.info("Jobul nu există, îl adăugăm...")
        scheduler.add_job(clean, "interval", days=1,
                          jobstore="default", id="clean_job", replace_existing=True)

    if not scheduler.running:
        try:
            register_events(scheduler)
            scheduler.start()
            logging.info("Scheduler started successfully!")
        except Exception as e:
            logging.error(f"Error starting scheduler: {e}")
    else:
        logging.info("Scheduler already running.")


# Asigură oprirea corectă la shutdown
def stop_scheduler():
    logging.info("Oprire APScheduler...")
    scheduler.shutdown()


atexit.register(stop_scheduler)
