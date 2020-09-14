import json
import requests
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from util import randomised_503


HOST_NAME = '0.0.0.0' # This will map to avialable port in docker
PORT_NUMBER = 8001
trees_api_url = "https://api.ecosia.org/v1/trees/count"

def fetch_tree_count():
	r = requests.get(trees_api_url)
	if r.status_code == 200:
		return r.json()['count']
	return 0



class HTTPRequestHandler(BaseHTTPRequestHandler):
    def get_treecounter(self):
        self.do_HEAD()
        tree_count = fetch_tree_count()
        bytes_tree_count = bytes("Ecosia tree counter: %d" % tree_count, 'utf-8')
        self.wfile.write(bytes_tree_count)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        if randomised_503(self): return
        endpoint = self.path
        if endpoint == '/treecounter':
            return self.get_treecounter()
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

if __name__ == '__main__':
    myServer = HTTPServer((HOST_NAME, PORT_NUMBER), HTTPRequestHandler)
    print(time.asctime(), 'Server Starts - %s:%s' % (HOST_NAME, PORT_NUMBER))
    try:
        myServer.serve_forever()
    except KeyboardInterrupt:
        pass
    myServer.server_close()
    print(time.asctime(), 'Server Stops - %s:%s' % (HOST_NAME, PORT_NUMBER))
