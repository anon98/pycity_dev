import http.server
import socketserver
import os

PORT = 8000

# Define handler to serve files from current directory
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

# Start the server
if __name__ == "__main__":
    web_dir = os.path.join(os.path.dirname(__file__), 'web')
    os.chdir(web_dir)

    handler = MyHandler
    httpd = socketserver.TCPServer(("", PORT), handler)

    print(f"Serving at port {PORT}")
    print(f"Open your browser and go to http://localhost:{PORT}/")
    httpd.serve_forever()
