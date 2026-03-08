from typing import Any, Optional

import docker
from docker.errors import DockerException
from .decorators import start

class Container(object):
    """
    Represents a Docker container.

    Attributes:
        client (docker.client.DockerClient): The Docker client.
        client_container (docker.models.containers.Container): The Docker container.
    """

    client: Optional[Any] = None
    client_container: Optional[Any] = None

    @classmethod
    def get_client(cls):
        if cls.client is None:
            try:
                cls.client = docker.from_env()
            except DockerException as exc:
                raise RuntimeError('Docker is not available') from exc

        return cls.client

    def get_container(self, name):
        """
        Retrieves a container by name.

        Args:
            name (str): The name of the container to retrieve.

        Returns:
            docker.models.containers.Container: The Docker container.
        """
        self.client_container = self.get_client().containers.get(name)
        return self

    def get_containers(self):
        """
        Retrieves a list of container names.

        Returns:
            list: A list of container names.
        """
        containers = [
            container.name for container in self.get_client().containers.list(all=True)]
        return containers

    def create_container(self, language, name, environment=False, key=None, value=None):
        """
        Create a Docker container with the specified image and name.

        Args:
            image (str): The name of the Docker image to use.
            name (str): The name to assign to the container.

        Returns:
            docker.models.containers.Container: The created Docker container.

        Raises:
            Exception: If an error occurs while creating the container.
        """
        images = {
            'python': {
                'container': 'python:3.9',
                'environment': {
                    'PYTHONPATH': f'/{name}/'
                }
            },
            'node': {
                'container': 'node:18.17.0',
                'environment': {
                    'NODE_PATH': f'/{name}/'
                }
            },
            'jmeter': {
                'container': 'jmeter:latest',
                'environment': {
                    'JMETER_HOME': f'/{name}/'
                }
            }
        }
        try:
            container_config = {
                'image': images[language]['container'],
                'tty': True,
                'stdin_open': True,
                'name': name,
            }

            if environment:
                language_config = images.get(language) or {}
                environment_config = language_config.get('environment')
                if environment_config:
                    container_config['environment'] = dict(environment_config)

            if key and value:
                existing_environment = container_config.get('environment')
                if isinstance(existing_environment, dict):
                    existing_environment.update({key: value})
                else:
                    container_config['environment'] = dict(images[language]['environment'])
                    container_config['environment'].update({key: value})
                    print(container_config)

            self.client_container = self.get_client().containers.create(
                **container_config)
            return self
        except Exception as e:
            return e
        
    def remove_container(self, name):
        """
        Remove a container by name.

        Args:
            name (str): The name of the container to remove.

        Returns:
            None
        """
        
        container = self.get_client().containers.get(name)
        container.remove(force=True)

    
    @start
    def run_command(self, command, path='/'):
        """
        Run a command in the specified path.

        Args:
            command (str): The command to execute.
            path (str): The path where the command should be run.

        Returns:
            tuple: A tuple containing the stdout (str), stderr (str), and return code (int) of the command.
        """
        
        if self.client_container is None:
            raise RuntimeError('Docker container is not available')

        exec_command = self.client_container.exec_run(
            command, demux=True, workdir=path)

        return exec_command[1][0], exec_command[1][1], exec_command[0]


    

