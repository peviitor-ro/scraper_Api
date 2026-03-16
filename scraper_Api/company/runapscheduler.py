import logging
import atexit
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django_apscheduler.models import DjangoJob

from .models import Company, DataSet
from jobs.models import Job

# Configurare logging
logging.basicConfig(level=logging.INFO)

# Global: scheduler-ul
scheduler = BackgroundScheduler(timezone="Europe/Bucharest")
scheduler.add_jobstore(DjangoJobStore(), "default")
PUBLISH_JOB_ID = "publish_pending_jobs"
CLEAN_JOB_ID = "clean_job"
JOB_LINK_TIMEOUT = 5
MAX_PUBLISH_WORKERS = 5


def unpublish_jobs(company):
    """Dezpublică toate joburile pentru o companie."""
    jobs = Job.objects.filter(company=company)
    for job in jobs:
        if job.published:
            job.unpublish()  # Presupunem că metoda salvează obiectul


def has_valid_location(job):
    remote_value = (job.remote or "").lower()
    has_remote = "remote" in remote_value
    has_locality = bool(job.city and job.county)
    return has_remote or has_locality


def is_job_link_available(job_link):
    if not job_link:
        return False

    try:
        response = requests.head(
            job_link,
            timeout=JOB_LINK_TIMEOUT,
            allow_redirects=True,
        )
        return response.ok
    except requests.RequestException as exc:
        logging.warning("Link indisponibil pentru %s: %s", job_link, exc)
        return False


def publish_company_jobs(company):
    logging.info("Verific joburile pentru compania %s", company.company)
    jobs = Job.objects.filter(company=company, published=False)
    published_count = 0

    for job in jobs.iterator():
        if not is_job_link_available(job.job_link):
            logging.info(
                "Jobul %s de la %s nu este disponibil",
                job.job_title,
                company.company,
            )
            continue

        if not has_valid_location(job):
            logging.info(
                "Jobul %s de la %s nu are locatie valida",
                job.job_title,
                company.company,
            )
            continue

        job.publish()
        published_count += 1

    logging.info(
        "%s joburi au fost publicate pentru compania %s",
        published_count,
        company.company,
    )
    return published_count


def publish_pending_jobs():
    logging.info("Jobul publish_pending_jobs() a inceput!")
    companies = Company.objects.filter(jobs__published=False).distinct()

    if not companies.exists():
        logging.info("Nu exista companii cu joburi nepublicate.")
        return

    total_published = 0
    with ThreadPoolExecutor(max_workers=MAX_PUBLISH_WORKERS) as executor:
        futures = {
            executor.submit(publish_company_jobs, company): company.company
            for company in companies
        }

        for future in as_completed(futures):
            company_name = futures[future]
            try:
                total_published += future.result()
            except Exception as exc:
                logging.exception(
                    "Eroare la publicarea joburilor pentru %s: %s",
                    company_name,
                    exc,
                )


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
    """Pornește APScheduler și adaugă joburile dacă nu există."""
    global scheduler

    # -------------------------
    # Job zilnic: clean()
    # -------------------------
    if not DjangoJob.objects.filter(id=CLEAN_JOB_ID).exists():
        logging.info("Jobul 'clean_job' nu există, îl programăm...")
        scheduler.add_job(
            clean,
            trigger="interval",
            days=1,  # Rulează zilnic
            id=CLEAN_JOB_ID,
            jobstore="default",
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=300,
        )
    else:
        logging.info("Jobul 'clean_job' există deja.")

    if not DjangoJob.objects.filter(id=PUBLISH_JOB_ID).exists():
        logging.info("Jobul 'publish_pending_jobs' nu exista, il programam...")
        scheduler.add_job(
            publish_pending_jobs,
            trigger="interval",
            days=1,  # Rulează zilnic
            id=PUBLISH_JOB_ID,
            jobstore="default",
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=300,
        )
    else:
        logging.info("Jobul 'publish_pending_jobs' exista deja.")

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
