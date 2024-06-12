from django.template.loader import render_to_string
from django.core.mail import send_mail
from .models import Newsletter
from jobs.models import Job
from django.db.models import Q
from time import sleep


def send_newsletter_mail(email, recommended_jobs):
    template = 'newsletter.html'

    context = {
        'email': email,
        'recommended_jobs': recommended_jobs,
    }

    subject = 'Jop postings update'
    message = render_to_string(template, context)
    email_from = 'cristi_olteanu@outlook.com'
    recipient_list = [email.email, ]
    send_mail(
        subject=subject,
        message="",
        from_email=email_from,
        recipient_list=recipient_list,
        html_message=message,
    )


def search():
    for newsletter in Newsletter.objects.all():
        filter_search = Q(published=False)

        if newsletter.job_title:
            filter_search &= Q(job_title__icontains=newsletter.job_title)

        if newsletter.city:
            cities = newsletter.city.split(",")
            filter_search &= Q(city__in=cities)

        if newsletter.company:
            companies = newsletter.company.split(",")
            filter_search &= Q(company__company__in=companies)

        if newsletter.job_type:
            filter_search &= Q(remote__icontains=newsletter.job_type)

        jobs = Job.objects.filter(filter_search)

        obj = [{"title": job.job_title, "link": job.job_link} for job in jobs]

        send_newsletter_mail(newsletter.email, obj)

        sleep(5)
