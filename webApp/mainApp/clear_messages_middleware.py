from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin

class ClearMessagesMiddleware(MiddlewareMixin):
    def process_request(self, request):
        storage = messages.get_messages(request)
        for _ in storage:
            pass
        storage.used = False
