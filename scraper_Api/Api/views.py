from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Scraper, TestLogs
import subprocess
import json
import os
import re
import requests

class ScraperView(APIView):
    extensions = {
        'py': 'python3',
        'js': 'node',
    }

    acceptedDirs = ['sites', 'spiders']

    def get(self, request, path,  format=None):
        scrapersFolder = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), 'scrapers/' + path)
            
        scrapers = dict()
        exclude = ['__init__.py']

        for root, _ , files in os.walk(scrapersFolder):
            if root.split('/')[-1] in self.acceptedDirs:
                for file in files:
                    if file not in exclude:
                        name = file.split('.')[0]
                        scrapers[name] = file
        if len(scrapers) == 0:
            return HttpResponse("Scraper not found", status=404)
        return Response([f"Total scrapers: {len(scrapers)}", scrapers])


    def post(self, request, path, format=None):

        scrapersFolder = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), 'scrapers/' + path)
        
        dir = ''
        
        for  root, _ , _ in os.walk(scrapersFolder):
            if root.split('/')[-1] in self.acceptedDirs:
                dir = root
                break

        file = request.data.get('file')
        update = request.data.get('update')
        status = request.data.get('status')
        force = request.data.get('force')

        log = dict()

        if file != None :
            scraperData = Scraper.objects.filter(name=file).first()
            if scraperData == None:
                scraperData = Scraper.objects.create(name=file)

            # to do: add scrapy crawl command
            try:
                command = self.extensions[file.split('.')[-1]]
                pattern = re.compile(r"\[([\s\S]*)\]")
            except KeyError:
                command = 'scrapy crawl'
                pattern = re.compile(r"\[([\s\S]*?)\]")

            try:
                process = subprocess.Popen([ com for com in command.split(' ')] + [file] , cwd=dir, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
                
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    try:
                        objects = json.loads(re.search(pattern, stdout.decode("utf8")).group(0))
                    except:
                        objects = stdout.decode("utf8").split('\n')
                    log['succes'] = objects
                    log["Total"] = len(objects)
                else:
                    log['error'] = stderr.decode("utf8").split('\n')
            except FileNotFoundError as e:
                log['error'] = "File not found"

            return Response(log)

        if update != None:
            process = subprocess.Popen(['git', 'pull', 'origin', 'main'], cwd=dir, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            log = dict()
            if process.returncode == 0:
                log['succes'] = stdout
            else:
                log['error'] = stderr
            return Response(log)
        
        if status != None :
            scraperData = Scraper.objects.filter(name=status).first()
            if scraperData == None:
                return Response({"status":"inactive"})
            logs = TestLogs.objects.filter(scraper=scraperData).order_by('-test_date')
            if len(logs) == 0 or logs[0].is_success == 'Pass':
                return Response({"status":"active"})
            else:
                return Response({"status":"inactive"})

        return Response('error')


class AddView(APIView):

    def post(self, request, format=None):
        url = request.data.get('url')

        path = os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), 'scrapers')
        
        log = dict()

        if url != None:
            repo = url.split('/')[-1].split('.git')[0]
            process = subprocess.Popen(
                ['git', 'clone', url], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            stdout, stderr = process.communicate()

            if process.returncode == 0:
                log["succes"] = stdout.decode("utf8") + "Repository cloned succesfully"
            else:
                log["error"] = stderr.decode("utf8")
             
            for file in os.listdir(os.path.join(path, repo)):
                
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

                if process.returncode == 0:
                    log['dependencies'] = stdout.decode("utf8") 
                else:
                    log['error'] = stderr.decode('utf-8')

            return Response(log)

        return Response('error')


class RemoveView(AddView):
    def get(self, request):
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

        if repo != None:
            process = subprocess.Popen(
                ['rm', '-rf', repo], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            log = dict()
            if process.returncode == 0:
                log['succes'] = "Repository removed succesfully"
            else:
                log['error'] = stderr.decode('utf-8')

            return Response(log)

        return Response('error')
    
@method_decorator(csrf_exempt, name='dispatch')
class LogsView(TemplateView):
    def get(self, request, path, scraper):
        template = 'logs.html'

        scrapersFolder = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), 'scrapers/' + path + "/sites")
        
        scraperList = list(map(lambda x: x.lower(), os.listdir(scrapersFolder)))
        
        if scraper.lower() not in scraperList:
            return HttpResponse("Scraper not found", status=404)
        else:
            scraperData = Scraper.objects.filter(name=scraper).first()

            if scraperData == None:
                scraperData = Scraper.objects.create(name=scraper)
            logs = TestLogs.objects.filter(scraper=scraperData).order_by('-test_date')

        context = {
            'scraper': scraperData,
            'logs': logs
        }

        return render(request, template, context)
    
    def post(self, request, path, scraper):
        scrapersFolder = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), 'scrapers/' + path + "/sites")
        
        scraperList = list(map(lambda x: x.lower(), os.listdir(scrapersFolder)))
    
        if scraper.lower() not in scraperList:
            return HttpResponse("Scraper not found", status=404)
        else:

            data = json.loads(request.body)
            logs = data.get('logs')
            is_success = data.get('is_success')
            
            choices = ["Pass", "Fail"]

            scraperData = Scraper.objects.filter(name=scraper).first()

            if scraperData == None:
                scraperData = Scraper.objects.create(name=scraper)

            if is_success not in choices:
                return HttpResponse("Invalid status", status=400)
            else:
                logs = TestLogs.objects.create(scraper=scraperData, test_result=logs, is_success=is_success)

            return redirect('logs', path=path, scraper=scraperData)

class PeviitorData(APIView):
    def post(self, request, format=None):
        company = request.data.get('company')
        if company != None:
            solr = f"https://solr.peviitor.ro/solr/jobs/select?indent=true&q.op=OR&q=company%3A%22{company}%22&rows=1000&useParams="
            response = requests.get(solr)
            data = {
                "succes": response.json().get('response').get('docs'),
                "Total": response.json().get('response').get('numFound')
            }

            return Response(data)
        return Response('error')