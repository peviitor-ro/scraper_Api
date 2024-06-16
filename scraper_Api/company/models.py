from django.db import models
from django.utils.timezone import datetime

class Company(models.Model):
    """
    Represents a company.

    Attributes:
        company (TextField): The name of the company.
        scname (CharField): The short name or abbreviation of the company (optional).
        website (CharField): The website URL of the company (optional).
        description (TextField): A description of the company (optional).
    """

    company = models.TextField(max_length=50)
    scname = models.CharField(max_length=50, blank=True)
    website = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.company
    

class DataSet(models.Model):
    """
    Represents a data set associated with a company.

    Attributes:
        company (Company): The company associated with the data set.
        date (DateField): The date of the data set.
        data (IntegerField): The data value of the data set.
    """

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='CompanyData')
    date = models.DateField(default=datetime.now())
    data = models.IntegerField()

    def __str__(self):
        return self.company.company


