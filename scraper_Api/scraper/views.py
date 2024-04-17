from rest_framework.response import Response
import re

from .utils.view import GenerivView
from .utils.scraper import Scraper
from .utils.container import Container
from .models import Scraper as ScraperModel

class ScraperAddView(GenerivView):
    """
    View for adding a scraper.

    This view handles the POST request for adding a scraper. It expects the 'url' and 'language'
    parameters in the request data. It creates a container, clones the repository from the provided
    URL, installs the dependencies, and returns the response.

    If either 'url' or 'language' is missing in the request data, it returns a 400 Bad Request response.
    If any exception occurs during the process, it also returns a 400 Bad Request response.
    """

    def post(self, request):
        url = request.data.get('url')
        language = request.data.get('language').lower()
        environment = request.data.get('isSystemVariable') or False

        response = dict()

        if not url or not language:
            return Response(status=400)

        try:
            name = url.split('/')[-1].split('.git')[0]
            container = Container().create_container(language, name, environment)
            scraper = Scraper(container)

            scraper_name = scraper.container.client_container.name

            response['container'] = scraper_name

            repository = scraper.clone_repository(url)
            response.update({'success': repository[1]}
                            if repository[-1] == 0
                            else {'error': repository[0]})

            dependencies = scraper.install_dependencies()
            response['dependencies'] = {
                'success': dependencies[0],
                'errors': dependencies[1]
            }

            

            scraper_query = ScraperModel.objects.create(
                name=scraper_name)
            request.user.scraper.add(scraper_query.id)
            return Response(response)

        except Exception:
            return Response(status=400)


class ScraperRemoveView(GenerivView):
    """
    View for removing a container.

    This view handles the HTTP POST request to remove a container.
    The container name is obtained from the request data and passed to the `remove_container` method of the `Container` class.
    If the container is successfully removed, a response with status code 200 is returned.
    If an exception occurs during the removal process, a response with status code 400 is returned.
    """

    def post(self, request):
        repo = request.data.get('name')
    
        try:
            scraper = request.user.scraper.get(name=repo)
            Container().remove_container(scraper.name)
            scraper.delete()

            return Response(status=200)
        except Exception:
            return Response(status=400)


class ScraperListView(GenerivView):
    """
    A view class for handling GET and POST requests related to scrapers.

    GET request returns a list of available scrapers in a specified path.
    POST request allows creating or updating a scraper.

    Attributes:
        None

    Methods:
        get: Handles GET requests and returns a list of available scrapers.
        post: Handles POST requests and creates or updates a scraper.
    """
    def get(self, request, path=None):

        try:
            scraper_name = request.user.scraper.get(name=path)
            container = Container().get_container(scraper_name.name)
            scraper = Scraper(container)
            folder = scraper.get_scraper_folder(scraper_name.name)

            exec_command = (container
                            .run_command('ls', f'/{scraper_name.name}/{folder}'))[0].decode('utf-8').split('\n')

            scrapers = {
                'total': len(exec_command),
                'files': [{
                    'name': file
                }
                    for file in exec_command if file.split('.')[-1] in scraper.extensions.keys()
                ]
            }

            return Response(scrapers)
        except Exception:
            return Response(status=404)

    def post(self, request, path):
        file = request.data.get('file')
        update = request.data.get('update')

        if not file and not update:
            return Response(status=400)
        try:
            scraper_name = request.user.scraper.get(name=path)
            container = Container().get_container(scraper_name.name)
  
            scraper = Scraper(container)
            folder = scraper.get_scraper_folder(scraper_name.name)

            response = dict()

            if file:
                try:
                    command = scraper.extensions[file.split('.')[-1]]
                    pattern = re.compile(r"\[([\s\S]*)\]")
                except KeyError:
                    command = 'scrapy crawl'
                    pattern = re.compile(r"\[([\s\S]*?)\]")

                response.update(scraper.run_scraper(
                    file, command, pattern, scraper_name.name, folder))

            if update:
                response.update(scraper.update_repository(scraper_name.name))

            return Response(response)

        except Exception:
            return Response(status=400)


