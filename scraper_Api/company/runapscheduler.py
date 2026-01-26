import logging
import atexit
import time
import os
import pysolr
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django_apscheduler.models import DjangoJob

from .models import Company, DataSet
from jobs.models import Job

# Configurare logging
logging.basicConfig(level=logging.INFO)

# Global: scheduler-ul
scheduler = BackgroundScheduler(timezone="Europe/Bucharest")
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


def run_flush_and_populate():
    """Flush Solr și repopulează joburile publicate."""
    logging.info("🧹 Jobul weekly Solr flush a început!")

    try:
        url = os.getenv("DATABASE_SOLR") + "/solr/jobs"
        username = os.getenv("DATABASE_SOLR_USERNAME")
        password = os.getenv("DATABASE_SOLR_PASSWORD")

        solr = pysolr.Solr(
            url=url,
            auth=(username, password),
            timeout=60,
        )

        jobs_qs = Job.objects.filter(published=True)

        jobs = [
            {
                "id": job.getJobId,
                "job_link": job.job_link,
                "job_title": job.job_title,
                "company": job.company.company,
                "country": job.country.split(","),
                "city": job.city.split(","),
                "county": job.county.split(","),
                "remote": job.remote.split(","),
            }
            for job in jobs_qs
        ]

        logging.info(f"Flushing and populating {len(jobs)} jobs to Solr")

        # Flush total
        solr.delete(q="*:*", commit=True)

        # Repopulare
        if jobs:
            solr.add(jobs, commit=True)

        logging.info("✅ Jobul weekly Solr flush s-a terminat cu succes!")

    except Exception as e:
        logging.error(f"❌ Eroare în jobul weekly Solr flush: {e}")


def start():
    """Pornește APScheduler și adaugă joburile dacă nu există."""
    global scheduler

    # -------------------------
    # Job zilnic: clean()
    # -------------------------
    if not DjangoJob.objects.filter(id="clean_job").exists():
        logging.info("Jobul 'clean_job' nu există, îl programăm...")
        scheduler.add_job(
            clean,
            trigger="interval",
            days=1,  # Rulează zilnic
            id="clean_job",
            jobstore="default",
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=300,
        )
    else:
        logging.info("Jobul 'clean_job' există deja.")

    # -------------------------
    # Job săptămânal: flush Solr
    # -------------------------
    if not DjangoJob.objects.filter(id="weekly_solr_flush").exists():
        logging.info("Jobul 'weekly_solr_flush' nu există, îl programăm...")
        scheduler.add_job(
            run_flush_and_populate,
            trigger=CronTrigger(day_of_week="sun", hour=3,
                                minute=30),  # Duminică la 03:30
            id="weekly_solr_flush",
            jobstore="default",
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=3600,  # 1 oră
        )
    else:
        logging.info("Jobul 'weekly_solr_flush' există deja.")

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
