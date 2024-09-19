from django.db import models

choices = (
    ('Python', 'Python'),
    ('JavaScript', 'JavaScript'),
    ('Jmeter', 'Jmeter'),
)


class Scraper (models.Model):
    name = models.CharField(max_length=50)
    language = models.CharField(
        max_length=50, choices=choices, default='Python')
    author = models.CharField(max_length=50, default='Anonymous')

    def __str__(self):
        return self.name
