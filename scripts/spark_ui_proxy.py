from http.server import BaseHTTPRequestHandler, HTTPServer
import http.client

class Proxy(BaseHTTPRequestHandler):
    def do_GET(self):
        conn = http.client.HTTPConnection("pedali-jupyter", 4041, timeout=30)
        try:
            conn.request("GET", self.path)
            response = conn.getresponse()
            body = response.read()
            self.send_response(response.status)
            for key, value in response.getheaders():
                if key.lower() not in ("connection", "transfer-encoding", "content-length"):
                    self.send_header(key, value)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        finally:
            conn.close()

HTTPServer(("0.0.0.0", 4041), Proxy).serve_forever()
