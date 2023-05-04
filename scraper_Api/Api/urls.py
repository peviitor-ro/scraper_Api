from django.urls import path, include
from . import views
import os

urlpatterns = [
    path('add/' , views.AddView.as_view()),
    path('remove/' , views.RemoveView.as_view()),
]

subfolders = [f.path for f in os.scandir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scrapers')) if f.is_dir() ]

for folder in subfolders:
    urlpatterns.append(path(folder.split('/')[-1]+'/', views.ScraperView.as_view()))

