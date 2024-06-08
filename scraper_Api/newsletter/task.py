from .views import send_newsletter_mail
from .models import Newsletter
from jobs.models import Job
from django.db.models import Q
from time import sleep


def search():
    for newsletter in Newsletter.objects.all():
        filter_search = Q(published=False)

        if newsletter.job_title:
            filter_search &= Q(job_title__icontains=newsletter.job_title)

        if newsletter.city:
            filter_search &= Q(city__icontains=newsletter.city)

        if newsletter.company:
            filter_search &= Q(
                company__company__icontains=newsletter.company)

        if newsletter.job_type:
            filter_search &= Q(remote__icontains=newsletter.job_type)

        jobs = Job.objects.filter(filter_search)

        obj = [{"title": job.job_title, "link": job.job_link} for job in jobs]

        send_newsletter_mail(newsletter.email, obj)

        sleep(5)
