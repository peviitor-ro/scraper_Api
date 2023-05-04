from rest_framework.response import Response  
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.views import APIView  
import os
import subprocess



class ApiView(APIView):
    
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
            subproces = subprocess.run([command , os.path.join(scrapersFolder, file)], capture_output=True, text=True)
            log = dict()
            if subproces.returncode == 0:
                log['succes'] = subproces.stdout
            else:
                log['error'] = subproces.stderr

            return Response(log)
        
        if update != None:
            subproces = subprocess.run(['git', 'pull', 'origin', 'main'], capture_output=True, text=True)
            log = dict()
            if subproces.returncode == 0:
                log['succes'] = subproces.stdout
            else:
                log['error'] = subproces.stderr
            return Response(log)
        
        return Response('error')
        