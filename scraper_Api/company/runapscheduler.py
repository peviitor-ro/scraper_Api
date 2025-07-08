import logging
import atexit
from django_apscheduler.models import DjangoJob
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from .models import Company, DataSet
from jobs.models import Job
import pymysql
from pymysql.err import OperationalError
import time

from dotenv import load_dotenv
import os
load_dotenv()


def get_connection():
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")

    """Return a MySQL connection."""
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=int(DB_PORT),
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
            print(f"[Retry {i + 1}] Conexiune pierdută: {e}")
            time.sleep(delay)

    raise OperationalError("Eroare: Nu s-a putut executa query-ul după retry-uri.")


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

    companies = get_all_companies()

    for company in companies:
        company = Company.objects.filter(company=company['company']).first()
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

if __name__ == "__main__":
    print(get_all_companies())
