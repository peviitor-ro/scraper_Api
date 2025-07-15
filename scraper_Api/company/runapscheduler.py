import logging
import atexit
import time
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django_apscheduler.models import DjangoJob
from .models import Company


from .models import Company, DataSet
from jobs.models import Job

# Configurare logging
logging.basicConfig(level=logging.INFO)

# Global: scheduler-ul
scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


def unpublish_jobs(company):
    """Dezpublică toate joburile pentru o companie."""
    jobs = Job.objects.filter(company=company)
    for job in jobs:
        if job.published:
            job.unpublish()  # Presupunem că metoda salvează obiectul


def clean():
    """Șterge companiile inactive sau dezpublică joburile vechi."""
    logging.info("Jobul clean() a început!")
    today = datetime.now().date()

    companies = Company.objects.values('company', 'source').distinct()

    for company_data in companies:
        company = Company.objects.filter(
            company=company_data['company']).first()
        if not company:
            continue

        last_data = DataSet.objects.filter(company=company).last()

        if not last_data or (today - last_data.date).days >= 2:
            if company.source:
                company.delete()
                logging.info(f"Compania {company.company} a fost ștearsă.")
            else:
                unpublish_jobs(company)
                logging.info(
                    f"Joburile pentru compania {company.company} au fost dezpublicate.")

    logging.info("Jobul clean() s-a încheiat cu succes!")


def start():
    """Pornește APScheduler și adaugă jobul dacă nu există."""
    global scheduler

    # Asigură-te că jobul nu e deja programat
    if not DjangoJob.objects.filter(id="clean_job").exists():
        logging.info("Jobul 'clean_job' nu există, îl programăm...")
        scheduler.add_job(
            clean,
            trigger="interval",
            minutes=1,  # Sau 'minutes=1' pentru test
            id="clean_job",
            jobstore="default",
            replace_existing=True,
        )
    else:
        logging.info("Jobul 'clean_job' există deja.")

    # Pornește schedulerul dacă nu e deja activ
    if not scheduler.running:
        try:
            register_events(scheduler)
            scheduler.start()
            logging.info("Schedulerul a fost pornit cu succes!")
        except Exception as e:
            logging.error(f"Eroare la pornirea schedulerului: {e}")
    else:
        logging.info("Schedulerul era deja pornit.")


def stop_scheduler():
    """Oprește în siguranță schedulerul la ieșirea din aplicație."""
    if scheduler.running:
        try:
            scheduler.shutdown()
            logging.info("Scheduler oprit cu succes.")
        except Exception as e:
            logging.error(f"Eroare la oprirea schedulerului: {e}")


# Înregistrăm funcția pentru oprire la shutdown
atexit.register(stop_scheduler)

# Dacă rulezi direct fișierul pentru test:
if __name__ == "__main__":
    logging.info("Pornim schedulerul...")
    start()
    try:
        while True:
            time.sleep(1)  # Menține scriptul activ
    except (KeyboardInterrupt, SystemExit):
        logging.info("Oprire manuală detectată, închidem schedulerul...")
        stop_scheduler()
