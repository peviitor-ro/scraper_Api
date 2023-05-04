from rest_framework.response import Response  
from rest_framework.views import APIView  
import os
import subprocess
from django.urls import clear_url_caches




class ScraperView(APIView):
    
    """
    API endpoint that allows users to be viewed or edited.
    """
    extensions = {
        'py': 'python',
        'js': 'node',
    }
    
    # permission_classes = [permissions.IsAuthenticated]
    def get(self, request, format=None):
        path = request.path.split('/')[2]

        scrapersFolder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scrapers/' + path + "/sites")
        scrapers = dict()
        exclude = ['__init__.py']
        for file in os.listdir(scrapersFolder):
            if file not in exclude:
                name = file.split('.')[0]
                scrapers[name] = file
        return Response(scrapers)
    
    def post(self, request, format=None):
        path = request.path.split('/')[2]

        scrapersFolder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scrapers/' + path + "/sites")

        file = request.data.get('file')
        update = request.data.get('update')

        if file != None:
            command = self.extensions[file.split('.')[-1]]
            process = subprocess.run([command , os.path.join(scrapersFolder, file)], capture_output=True)
            log = dict()
            if process.returncode == 0:
                log['succes'] = process.stdout
            else:
                log['error'] = process.stderr

            return Response(log)
        
        if update != None:
            process = subprocess.run(['git', 'pull', 'origin', 'main'], capture_output=True, text=True)
            log = dict()
            if process.returncode == 0:
                log['succes'] = process.stdout
            else:
                log['error'] = process.stderr
            return Response(log)
        
        return Response('error')
    
class AddView(APIView):
    
    def post (self, request, format=None):
        url = request.data.get('url')
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scrapers')
        
        if url != None:
            process = subprocess.Popen(['git', 'clone', url], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            log = dict()
            if process.returncode == 0:
                log['succes'] = stdout.decode('utf-8') + 'succes'
            else:
                log['error'] = stderr.decode('utf-8')

            return Response(log)
        
        clear_url_caches()
        
        return Response('error')
    
class RemoveView(AddView):
    def get (self, request):
        folders = [f.path for f in os.scandir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scrapers')) if f.is_dir() ]
        return Response(folders)
        