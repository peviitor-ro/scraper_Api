
import json
import re


class Scraper(object):
    """
    A class representing a scraper.

    Attributes:
        extensions (dict): A dictionary mapping file extensions to their corresponding execution commands.
        accepted_dirs (list): A list of accepted directory names.
        dependencies (list): A list of dependency file names.
        container (object): The container object used for running commands.

    Methods:
        __init__(self, container): Initializes a Scraper object.
        clone_repository(self, url): Clones a repository from the given URL.
        install_dependencies(self): Installs the required dependencies.
        get_scraper_folder(self, path): Retrieves the scraper folder from the given path.
        run_scraper(self, file, command, pattern, path, folder): Runs the scraper with the specified parameters.
        update_repository(self, path): Updates the repository at the given path.
    """

    extensions = {
        'py': 'python3',
        'js': 'node',
        'jmx': 'jmeter -n -t',
    }
    accepted_dirs = ['sites', 'spiders']
    dependencies = ['requirements.txt', 'package.json', 'setup.py']

    def __init__(self, container):
        """
        Initializes a Scraper object.

        Args:
            container (object): The container object used for running commands.
        """
        self.container = container

    def clone_repository(self, url):
        """
        Clones a repository from the given URL.

        Args:
            url (str): The URL of the repository to clone.

        Returns:
            exec_command (str): The execution command for cloning the repository.
        """
        exec_command = (self.container
                        .run_command(command=f'git clone {url}'))
        return exec_command

    def install_dependencies(self):
        """
        Installs the required dependencies.

        Returns:
            exec_command (str): The execution command for installing the dependencies.
        """
        dependecies_commands = {
            'requirements.txt': 'pip3 install -r requirements.txt',
            'package.json': 'npm i',
            'setup.py': 'python3 setup.py develop'
        }

        exec_command = (
            self.container
            .run_command(command='ls', path=f'/{self.container.client_container.name}')
        )[0].decode('utf-8').split('\n')

        dependencies_file = "".join(
            [file for file in exec_command if file in self.dependencies])

        exec_command = (self.container
                        .run_command(
                            command=dependecies_commands[dependencies_file],
                            path=f'/{self.container.client_container.name}'))

        return exec_command

    def get_scraper_folder(self, path):
        """
        Retrieves the scraper folder from the given path.

        Args:
            path (str): The path to search for the scraper folder.

        Returns:
            folder (str): The name of the scraper folder.
        """
        exec_command = (self.container
                        .run_command(command='ls', path=f'/{path}'))[0].decode('utf-8').split('\n')

        scrapers_folder = [
            folder for folder in exec_command if folder in self.accepted_dirs]

        folder = "".join(scrapers_folder)

        return folder

    def run_scraper(self, file, command, pattern, path, folder):
        """
        Runs the scraper with the specified parameters.

        Args:
            file (str): The file to run the scraper on.
            command (str): The execution command for running the scraper.
            pattern (str): The pattern to search for in the scraper output.
            path (str): The path to the scraper folder.
            folder (str): The name of the scraper folder.

        Returns:
            response (dict): A dictionary containing the execution response.
        """
        response = dict()
        try:
            exec_command = (self.container
                            .run_command(command=f'{command} {file}', path=f'/{path}/{folder}'))

            if exec_command[-1] == 0:
                stdout = exec_command[0].decode('utf-8').strip()

                try:
                    objects = json.loads(
                        re.search(pattern, stdout.replace("<Response [200]>", "")).group(0))
                except Exception:
                    objects = stdout.split('\n')
                response['success'] = objects
                response["Total"] = len(objects)
            else:
                stderr = exec_command[1].decode('utf-8')
                response['error'] = stderr

        except Exception:
            response['error'] = "File not found"

        return response

    def update_repository(self, path):
        """
        Updates the repository at the given path.

        Args:
            path (str): The path to the repository.

        Returns:
            response (dict): A dictionary containing the execution response.
        """
        exec_command = self.container.run_command(
            command='git pull origin main', path=f'/{path}')

        response = dict()
        if exec_command[-1] == 0:
            stdout = exec_command[0].decode('utf-8')
            response['success'] = stdout
        else:
            stderr = exec_command[1].decode('utf-8')
            response['error'] = stderr

        return response
