import json
import requests
from string import Template
import time
import random
from http.server import BaseHTTPRequestHandler, HTTPServer
from util import artificial_503, artificial_latency


HOST_NAME = '0.0.0.0' # This will map to avialable port in docker
PORT_NUMBER = 8001
trees_api_url = "https://api.ecosia.org/v1/trees/count"
with open('./templates/treeCounter.html', 'r') as f:
    html_string = f.read()
html_template = Template(html_string)

def fetch_tree_count():
       r = requests.get(trees_api_url) if random.random() > 0.15 else artificial_503()
       if r.status_code == 200:
               return r.json()['count']
       return 0



class HTTPRequestHandler(BaseHTTPRequestHandler):

    @artificial_latency
    def get_treecounter(self):
        self.do_HEAD()
        tree_count = fetch_tree_count()
        bytes_template = bytes(html_template.substitute(counter=tree_count), 'utf-8')
        self.wfile.write(bytes_template)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        endpoint = self.path
        if endpoint == '/treecounter':
            return self.get_treecounter()
        else:
            self.send_error(404)

if __name__ == '__main__':
    myServer = HTTPServer((HOST_NAME, PORT_NUMBER), HTTPRequestHandler)
    print(time.asctime(), 'Server Starts - %s:%s' % (HOST_NAME, PORT_NUMBER))
    try:
        myServer.serve_forever()
    except KeyboardInterrupt:
        pass
    myServer.server_close()
    print(time.asctime(), 'Server Stops - %s:%s' % (HOST_NAME, PORT_NUMBER))
