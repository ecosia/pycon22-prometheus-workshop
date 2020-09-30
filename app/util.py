import random

def randomised_503(request_handler):
    random_number = random.random()
    if random_number < 0.15:
        request_handler.send_response(503, 'Fake 503 (service available) response')
        request_handler.send_header('Content-type', 'text/html')
        request_handler.end_headers()
        return True
    else:
        return False
