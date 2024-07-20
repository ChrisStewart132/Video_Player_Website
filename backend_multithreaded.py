import http.server
import socketserver
from os.path import getsize, join, isfile
import os

PORT = 8000
VIDEO_DIR = "docs/assets/videos"
DOCS_DIR = "docs"

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Handle GET request
        if self.path == '/' or self.path == '/index.html':
            self._get_web_page()
        elif self.path == '/api/video_count':
            self._get_video_count()
        elif self.path.startswith('/api/get_video/'):
            self._get_video(self.path.split("/")[-1])
        else:
            self.send_error(404, "File not found")
    
    def do_POST(self):
        # Handle POST request
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # For now, just respond with the received data
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(post_data[:10])

    def _get_web_page(self):
        try:
            web_page_path = join(DOCS_DIR, "index.html")
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Content-Length', getsize(web_page_path))
            self.end_headers()
            with open(web_page_path, 'r', encoding='utf-8') as file:
                response_data = file.read().encode('utf-8')
                self.wfile.write(response_data)
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")

    def _get_video_count(self):
        try:
            video_files = [f for f in os.listdir(VIDEO_DIR) if isfile(join(VIDEO_DIR, f)) and f.endswith('.mp4')]
            n = len(video_files)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(f'{{"video_count": {n}}}', 'utf-8'))
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def _get_video(self, i):
        try:
            i = int(i)  # raises ValueError if i is not an integer.
            video_files = [f for f in os.listdir(VIDEO_DIR) if isfile(join(VIDEO_DIR, f)) and f.endswith('.mp4')]
            if 0 <= i < len(video_files):
                video_file = join(VIDEO_DIR, video_files[i])
                self.send_response(200)
                self.send_header('Content-type', 'video/mp4')
                self.send_header('Content-Length', getsize(video_file))
                self.end_headers()
                with open(video_file, 'rb') as file:
                    self.wfile.write(file.read())
            else:
                self.send_error(404, "Video not found")
        except ValueError:
            self.send_error(400, "Invalid video index")
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")

# Create an object of the above class
handler_object = MyHttpRequestHandler

# Define the server class with threading
class ThreadingSimpleServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    pass

# Create a ThreadingSimpleServer object, passing in the handler object
with ThreadingSimpleServer(("", PORT), handler_object) as httpd:
    server_address = httpd.server_address
    ip_address = server_address[0] if server_address[0] != '' else '127.0.0.1'
    port = server_address[1]
    print(f"Server started at http://{ip_address}:{port}")
    httpd.serve_forever()
