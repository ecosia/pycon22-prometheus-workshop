import random
from requests import Response
from time import sleep

def artificial_503():
    r = Response()
    r.status_code = 503
    r.reason = "Uh oh - artificial 503"
    r.json = {}
    return r


def artificial_latency(func):
    def randomised_latency(request_handler):
        random_number = random.random()
        sleep(random_number)
        return func(request_handler)
    return randomised_latency
