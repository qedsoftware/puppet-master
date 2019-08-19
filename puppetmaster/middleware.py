from django.contrib.auth import login


class AutoLoginMiddleware:
    user = None

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self.user is not None:
            login(request, self.user)
        return self.get_response(request)
