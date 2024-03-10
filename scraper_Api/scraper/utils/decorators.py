def start(func):
    """
    Decorator that starts the client container before executing the decorated function,
    and stops the client container after the execution is complete.
    """
    def wrapper(self, *args, **kwargs):
        self.client_container.start()
        execute = func(self, *args, **kwargs)
        self.client_container.stop()
        return execute
    return wrapper