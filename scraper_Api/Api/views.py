from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Scraper, TestLogs, DataSet
from .serializer import DataSetSerializer

from datetime import datetime, timedelta
import subprocess
import json
import os
import re

SCRAPER_PATH = 'scrapers'
not_found_message = "Scraper not found"

def get_scrapers(folder): 
    path = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), SCRAPER_PATH + '/' + folder)
    scrapers = dict()
    exclude = ['__init__.py']

    accepted_dirs = ['sites', 'spiders']

    for root, _ , files in os.walk(path):
        if root.split('/')[-1] in accepted_dirs:
            for file in files:
                if file not in exclude:
                    name = file.split('.')[0]
                    scrapers[name] = file
    return scrapers

class ScraperView(APIView):

    extensions = {
        'py': 'python3',
        'js': 'node',
        'jmx': 'jmeter -n -t',
    }

    acceptedDirs = ['sites', 'spiders']

    def get(self, _ , path,  format=None):
            scrapers = get_scrapers(path)
            if len(scrapers) == 0:
                return HttpResponse(not_found_message, status=404)
            return Response([f"Total scrapers: {len(scrapers)}", scrapers])

    def post(self, request, path, format=None):
            path = os.path.join(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__))), SCRAPER_PATH + '/' + path)
            
            dir_name = ''
            
            for  root, _ , _ in os.walk(path):
                if root.split('/')[-1] in self.acceptedDirs:
                    dir_name = root
                    break

            file = request.data.get('file')
            update = request.data.get('update')

            log = dict()

            if file != None :

                # to do: add scrapy crawl command
                try:
                    command = self.extensions[file.split('.')[-1]]
                    pattern = re.compile(r"\[([\s\S]*)\]")
                except KeyError:
                    command = 'scrapy crawl'
                    pattern = re.compile(r"\[([\s\S]*?)\]")

                log.update(self.run_scraper(dir_name, file, command, pattern))

                return Response(log)

            if update != None:
                log = self.update_repository(dir_name)
                return Response(log)

            return Response('error')
    
    def run_scraper(self, dir_name, file , command, pattern):
        log = dict()
        try:
            process = subprocess.Popen([ com for com in command.split(' ')] + [file] , cwd=dir_name, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                try:
                    objects = json.loads(
                        # to do:Add remove elements in database
                        re.search(pattern, stdout.decode("utf8").replace("<Response [200]>","")
                                ).group(0))
                except Exception:
                    objects = stdout.decode("utf8").split('\n')
                log['succes'] = objects
                log["Total"] = len(objects)
            else:
                log['error'] = stderr.decode("utf8").split('\n')

        except FileNotFoundError:
            log['error'] = "File not found"

        return log
    
    def update_repository(self, dir_name):
        process = subprocess.Popen(['git', 'pull', 'origin', 'main'], cwd=dir_name, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        log = dict()
        if process.returncode == 0:
            log['succes'] = stdout
        else:
            log['error'] = stderr

        return log

class AddView(APIView):
    def get(self, request, format=None):
        folders = [f.path for f in os.scandir(os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), 'scrapers')) if f.is_dir()]
        repos = list()
        for folder in folders:
            repos.append(folder.split('/')[-1])

        return Response(repos)

    def post(self, request, format=None):
        url = request.data.get('url')

        path = os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), 'scrapers')
        
        log = dict()

        if url != None:
            log.update(self.clone_repository(url, path))
            repo = url.split('/')[-1].split('.git')[0]
            log.update(self.install_dependencies(path, repo))

            return Response(log)

        return Response('error')
    
    def clone_repository(self, url, path):
        log = dict()
        
        process = subprocess.Popen(
            ['git', 'clone', url], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = process.communicate()

        if process.returncode == 0:
            log["succes"] = stdout.decode("utf8") + "Repository cloned succesfully"
        else:
            log["error"] = stderr.decode("utf8")

        return log
    
    def install_dependencies(self, path, repo):
        log = dict()
        for file in os.listdir(os.path.join(path, repo)): 
            process = None
            if file == "setup.py":
                process = subprocess.Popen(['python3', file, 'develop'], cwd=os.path.join(
                    path, repo), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                stdout, stderr = process.communicate()

            elif file == "requirements.txt":
                process = subprocess.Popen(['pip3', 'install', '-r', file], cwd=os.path.join(
                    path, repo), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                stdout, stderr = process.communicate()

            elif file == "package.json":
                process = subprocess.Popen(['npm', 'i'], cwd=os.path.join(
                    path, repo), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
                stdout, stderr = process.communicate()

            if process and process.returncode == 0:
                log['dependencies'] = stdout.decode("utf8")   
            else:
                log['error'] = stderr.decode("utf8") 

        return log

class RemoveView(AddView):
    def get(self, request, format=None):
        folders = [f.path for f in os.scandir(os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), 'scrapers')) if f.is_dir()]
        repos = list()
        for folder in folders:
            repos.append(folder.split('/')[-1])

        return Response(repos)

    def post(self, request, format=None):
        repo = request.data.get('repo')
        path = os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), 'scrapers')

        log = dict()
        if repo != None:
            log.update(self.delete_repository(repo, path))

            return Response(log)

        return Response('No repository selected')
    
    def delete_repository(self, repo, path):
        process = subprocess.Popen(
            ['rm', '-rf', repo], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _ , stderr = process.communicate()

        log = dict()
        if process.returncode == 0:
            log['succes'] = "Repository removed succesfully"
        else:
            log['error'] = stderr.decode('utf-8')

        return log
    
@method_decorator(csrf_exempt, name='dispatch')
class LogsView(TemplateView):
    def get(self, request, path, scraper):
        template = 'logs.html'

        path = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), 'scrapers/' + path + "/sites")
        
        scraper_list = list(map(lambda x: x.lower(), os.listdir(path)))
        
        if scraper.lower() not in scraper_list:
            return HttpResponse(not_found_message, status=404)
        else:
            scraper_data = Scraper.objects.filter(name=scraper).first()

            if scraper_data == None:
                scraper_data = Scraper.objects.create(name=scraper)
            logs = TestLogs.objects.filter(scraper=scraper_data).order_by('-test_date')

        context = {
            'scraper': scraper_data,
            'logs': logs
        }

        return render(request, template, context)
    
    def post(self, request, path, scraper):
        path = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), 'scrapers/' + path + "/sites")
        
        scraper_list = list(map(lambda x: x.lower(), os.listdir(path)))
    
        if scraper.lower() not in scraper_list:
            return HttpResponse(not_found_message, status=404)
        else:

            data = json.loads(request.body)
            logs = data.get('logs')
            is_success = data.get('is_success')
            
            choices = ["Pass", "Fail"]

            scraper_data = Scraper.objects.filter(name=scraper).first()

            if scraper_data == None:
                scraper_data = Scraper.objects.create(name=scraper)

            if is_success not in choices:
                return HttpResponse("Invalid status", status=400)
            else:
                logs = TestLogs.objects.create(scraper=scraper_data, test_result=logs, is_success=is_success)

            return redirect('logs', path=path, scraper=scraper_data)
    
class DataSetView(APIView):
    def get(self, request, path, scraper, format=None):
        scraper_data = Scraper.objects.filter(name=scraper).first()

        if scraper_data == None:
            scraper_name = scraper.split('.')[0]
            if get_scrapers(path).get(scraper_name) == None:
                return HttpResponse(not_found_message, status=404)
            else:
                Scraper.objects.create(name=scraper)
                scraper_data = Scraper.objects.filter(name=scraper).first()

        # get last 30 days  
        current_date = datetime.now()
        last_30_days = current_date - timedelta(days=30)
        data = DataSet.objects.filter(scraper=scraper_data, date__gte=last_30_days).order_by('date')

        serializer = DataSetSerializer(data, many=True)
        return Response(serializer.data)
    
    def post(self, request, path, scraper, format=None):
        scraper_data = Scraper.objects.filter(name=scraper).first()

        if scraper_data == None:
            scraper_name = scraper.split('.')[0]
            if get_scrapers(path).get(scraper_name) == None:
                return HttpResponse(not_found_message, status=404)
            else:
                Scraper.objects.create(name=scraper)
                scraper_data = Scraper.objects.filter(name=scraper).first()
        
        data = request.data.get('data')
        if data != None:
            from datetime import datetime
            current_date = datetime.now()

            DataSet.objects.update_or_create(scraper=scraper_data ,date=current_date, defaults={'data': data})

            return Response("succes")
        return Response('error')
    
    
