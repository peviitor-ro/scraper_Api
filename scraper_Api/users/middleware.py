from django.http import HttpResponseForbidden
from django.utils import timezone

class RateLimitMiddleware:
    """
    Middleware class to implement rate limiting based on IP address.

    This middleware checks the IP address of incoming requests and limits the rate of requests
    from the same IP address to prevent abuse or excessive usage.

    Attributes:
        get_response (function): The next middleware or view function in the chain.
        requests (dict): A dictionary to store the timestamp of each request made by an IP address.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.requests = {}

    def __call__(self, request):
        if request.path == "/":
            ip_address = request.META.get('REMOTE_ADDR')
            current_time = timezone.now()

            if ip_address in self.requests:
                if (current_time - self.requests[ip_address]).seconds < 10:
                    return HttpResponseForbidden()
                
            self.requests[ip_address] = current_time

        response = self.get_response(request)
        return response