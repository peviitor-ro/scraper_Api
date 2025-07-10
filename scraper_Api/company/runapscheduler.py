import logging
import atexit
import os
import time
from datetime import datetime

from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django_apscheduler.models import DjangoJob
from pymysql.err import OperationalError
import pymysql

from .models import Company, DataSet
from jobs.models import Job

# Configurare logging
logging.basicConfig(level=logging.INFO)

# Încarcă variabilele de mediu
load_dotenv()

# Global: scheduler-ul
scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


def get_connection():
    """Return a MySQL connection."""
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT")),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def get_all_companies(retries=3, delay=2):
    """Return all companies, cu retry logic pentru conexiuni pierdute."""
    for i in range(retries):
        try:
            connection = get_connection()
            connection.ping(reconnect=True)

            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM company_company")
                results = cursor.fetchall()
                connection.close()
                return results

        except OperationalError as e:
            logging.warning(f"[Retry {i + 1}] Conexiune pierdută: {e}")
            time.sleep(delay)

    raise OperationalError(
        "Eroare: Nu s-a putut executa query-ul după retry-uri.")


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

    companies = get_all_companies()

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
            days=1,  # Sau 'minutes=1' pentru test
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
    companies = get_all_companies()
    print(f"{len(companies)} companii extrase.")
