from django.urls import path, include
from rest_framework import routers
from . import views
import os

urlpatterns = [
    
]

subfolders = [f.path for f in os.scandir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scrapers')) if f.is_dir() ]

for folder in subfolders:
    urlpatterns.append(path(folder.split('/')[-1]+'/', views.ApiView.as_view()))

