from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Scraper, TestLogs, DataSet
from .serializer import DataSetSerializer

from datetime import datetime, timedelta
from datetime import datetime
import json
import os
import re

from .utils.getScrapers import get_scrapers
from .utils.process import run_process
from .constants import SCRAPER_PATH

not_found_message = "Scraper not found"

class ScraperView(APIView):
    extensions = {
        'py': 'python3',
        'js': 'node',
        'jmx': 'jmeter -n -t',
    }
    acceptedDirs = ['sites', 'spiders']

    def get(self, _ , path,  format=None):
        scrapers = get_scrapers(path)

        response = [
            f"Total scrapers: {len(scrapers)}",
            scrapers
        ]
        status = 200

        if not len(scrapers):
            status = 404
            response = not_found_message
            
        return Response(response, status=status)

    def post(self, request, path, format=None):
        path = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)
                )
            ), SCRAPER_PATH + '/' + path)
        
        dir_name = ''
        
        for  root, _ , _ in os.walk(path):
            if root.split('/')[-1] in self.acceptedDirs:
                dir_name = root
                break

        file = request.data.get('file')
        update = request.data.get('update')

        if not file and not update:
            return Response("Invalid request", status=400)

        response = dict()

        if file:
            try:
                command = self.extensions[file.split('.')[-1]]
                pattern = re.compile(r"\[([\s\S]*)\]")
            except KeyError:
                command = 'scrapy crawl'
                pattern = re.compile(r"\[([\s\S]*?)\]")

            response.update(self.run_scraper(dir_name, file, command, pattern))

        if update:
            response = self.update_repository(dir_name)

        return Response(response)
    
    def run_scraper(self, dir_name, file , command, pattern):
        response = dict()
        try:
            stdout, stderr , returncode = run_process([ com for com in command.split(' ')] + [file], dir_name)
            if returncode == 0:
                try:
                    objects = json.loads(
                        re.search(pattern, stdout.replace("<Response [200]>","")).group(0))
                except Exception:
                    objects = stdout.split('\n')
                response['success'] = objects
                response["Total"] = len(objects)
            else:
                response['error'] = stderr.split('\n')

        except FileNotFoundError:
            response['error'] = "File not found"

        return response
    
    def update_repository(self, dir_name):
        stdout, stderr , returncode = run_process(['git', 'pull', 'origin', 'main'], dir_name)

        response = dict()
        if returncode == 0:
            response['success'] = stdout
        else:
            response['error'] = stderr

        return response

# generic scraper class
class Scraper(object):
    """
    Class representing a scraper object.

    Methods:
    - get: Retrieves the list of folders from the specified path.
    - get_folders: Retrieves the list of folders from the specified path.

    Attributes:
    - None
    """
    def get(self, _):
        repos = self.get_folders(SCRAPER_PATH)
        return Response(repos) 
    
    def get_folders(self, path):
        folders = [f.path for f in os.scandir(os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), path)) if f.is_dir()]
        
        repos = [folder.split('/')[-1] for folder in folders]

        return repos
    
class AddView(APIView, Scraper):
    def post(self, request):
        url = request.data.get('url')

        path = os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), SCRAPER_PATH)
        
        response = dict()

        if not url:
            return Response(status=400)
        
        try:
            response.update(self.clone_repository(url, path))
            repo = url.split('/')[-1].split('.git')[0]
            response.update(self.install_dependencies(path, repo))

            return Response(response)
        
        except Exception:
            return Response("Invalid url", status=400)

    def clone_repository(self, url, path):
        response = dict()

        stdout, stderr, returncode = run_process(['git', 'clone', url], path)

        if returncode == 0:
            response["success"] = stdout + "Repository cloned succesfully"
        else:
            response["error"] = stderr

        return response
    
    def install_dependencies(self, path, repo):
        dependecies = {
            'requirements.txt': 'pip3 install -r requirements.txt',
            'package.json': 'npm i',
            'setup.py': 'python3 setup.py develop'
        }
        response = dict()
        for file in os.listdir(os.path.join(path, repo)): 
            try:
                command = dependecies[file]
                stdout, stderr , returncode = run_process(
                    [com for com in command.split(' ')], 
                    os.path.join(path, repo)
                )

                if returncode == 0:
                    response['dependencies'] = stdout  
                else:
                    response['error'] = stderr

                break
            except KeyError:
                continue
        return response

class RemoveView(AddView, Scraper):
    def post(self, request):
        repo = request.data.get('repo')
        path = os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), SCRAPER_PATH)

        response = dict()
        if repo != None:
            response.update(self.delete_repository(repo, path))

            return Response(response)

        return Response('No repository selected')
    
    def delete_repository(self, repo, path):
        _ , stderr , returncode = run_process(['rm', '-rf', repo], path)

        response = dict()
        if returncode == 0:
            response['success'] = "Repository removed succesfully"
        else:
            response['error'] = stderr

        return response
    
@method_decorator(csrf_exempt, name='dispatch')
class LogsView(TemplateView):
    scrapers_path = "sites"
    template = 'responses.html'
    def get(self, request, path, scraper):
        scraper_list = self.get_scrapers(path)
        
        if scraper.lower() not in scraper_list:
            return Response(not_found_message, status=404)
        else:
            scraper_data = Scraper.objects.filter(name=scraper).first()

            if scraper_data == None:
                scraper_data = Scraper.objects.create(name=scraper)
            responses = TestLogs.objects.filter(scraper=scraper_data).order_by('-test_date')

        context = {
            'scraper': scraper_data,
            'responses': responses
        }

        return render(request, self.template, context)
    
    def post(self, request, path, scraper):
        scraper_list = self.get_scrapers(path)
    
        if scraper.lower() not in scraper_list:
            return Response(not_found_message, status=404)
        else:
            data = json.loads(request.body)
            responses = data.get('responses')
            is_success = data.get('is_success')
            
            choices = ["Pass", "Fail"]

            scraper_data = Scraper.objects.filter(name=scraper).first()

            if not scraper_data :
                scraper_data = Scraper.objects.create(name=scraper)

            if is_success not in choices:
                return Response("Invalid status", status=400)
            else:
                responses = TestLogs.objects.create(scraper=scraper_data, test_result=responses, is_success=is_success)

            return redirect('responses', path=path, scraper=scraper_data)
        
    def get_scrapers(self, path):
        path = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), SCRAPER_PATH + '/' + path + "/" + self.scrapers_path)
        
        scraper_list = list(map(lambda x: x.lower(), os.listdir(path)))

        return scraper_list
    
class DataSetView(APIView):
    def get(self, _, path, scraper):
        scraper_data = self.get_or_create_scraper(path, scraper)

        if not scraper_data:
            scraper_name = scraper.split('.')[0]
            if get_scrapers(path).get(scraper_name) == None:
                return Response(not_found_message, status=404)
            else:
                Scraper.objects.create(name=scraper)
                scraper_data = Scraper.objects.filter(name=scraper).first()

        # get last 30 days  
        current_date = datetime.now()
        last_30_days = current_date - timedelta(days=30)
        data = DataSet.objects.filter(scraper=scraper_data, date__gte=last_30_days).order_by('date')

        serializer = DataSetSerializer(data, many=True)
        return Response(serializer.data)
    
    def post(self, request, path, scraper):
        scraper_data = self.get_or_create_scraper(path, scraper)
        data = request.data.get('data')

        if not data:
            return Response("Invalid request", status=400)
        
        current_date = datetime.now()
        DataSet.objects.update_or_create(scraper=scraper_data ,date=current_date, defaults={'data': data})

        return Response(status=201)
    
    def get_or_create_scraper(self, path, scraper):
        scraper_data = Scraper.objects.filter(name=scraper).first()

        if not scraper_data:
            scraper_name = scraper.split('.')[0]
            if get_scrapers(path).get(scraper_name) == None:
                return Response(not_found_message, status=404)
            else:
                Scraper.objects.create(name=scraper)
                scraper_data = Scraper.objects.filter(name=scraper).first()

        return scraper_data
        
    
    
