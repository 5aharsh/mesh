from libs.server import FilerHandler
from http.server import ThreadingHTTPServer

def run(server_class=ThreadingHTTPServer, handler_class=FilerHandler):
    server_address = ('', 8000)
    print("Serving at http://localhost:8000")
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

try:
    run()
except(KeyboardInterrupt):
    print("Server stopped")