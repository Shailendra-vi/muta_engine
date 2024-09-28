import time
import logging


logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    """
    Middleware to log the details of each request and its response.
    It logs the request method, path, and the response status code.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        logger.info(f"Incoming request: {request.method} {request.path}")
        response = self.get_response(request)

        duration = time.time() - start_time
        logger.info(f"Response: {response.status_code} for {request.method} {request.path} (Duration: {duration:.2f}s)")

        return response
