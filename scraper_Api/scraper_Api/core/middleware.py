from django.urls import resolve

class ViewLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        resolver_match = resolve(request.path_info)

        view_name = resolver_match.view_name 

        print("=== VIEW CALLED ===")
        print(f"Path: {request.path}")
        print(f"View name: {view_name}")
        print("===================")

        response = self.get_response(request)
        return response