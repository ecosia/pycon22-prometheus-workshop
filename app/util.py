import random
from time import sleep


def generate_5xx(func):
    def randomised_503(request_handler):
        random_number = random.random()
        if not random_number < 0.15:
            return func(request_handler)
        request_handler.send_response(503, 'Fake 503 (service available) response')
        request_handler.send_header('Content-type', 'text/html')
        request_handler.end_headers()
    return randomised_503

def artificial_latency(func):
    def randomised_latency(request_handler):
        random_number = random.random()
        sleep(random_number)
        return func(request_handler)
    return randomised_latency
