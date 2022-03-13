from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import yaml
import sys
import traceback

with open("../Deploy/resources/env-dev.yml", "r") as stream:
    try:
        env = yaml.safe_load(stream)
        os.environ['RDS_USERNAME'] =  env['RDS_SESSION_USERNAME']
        os.environ['RDS_PASSWORD'] = env['RDS_SESSION_PASSWORD']
        os.environ['RDS_HOST'] = env['RDS_HOST']
        os.environ['RDS_DEFAULT_DB'] = env['RDS_DEFAULT_DB']
        os.environ['SESSION_EXPIRATION_MINUTE'] = str(env['SESSION_EXPIRATION_MINUTE'])
    except yaml.YAMLError as exc:
        print(exc)

sys.path.append(os.path.abspath('../Order'))
import order
import ping
import status
import session
import item
import response


class LocalServerRouter(BaseHTTPRequestHandler):
    def do_GET(self):
        return_response = response.failure("Error or unsupported operations")
        event = {"Session" : self.headers['Session']}
        context = {}

        try:
            if self.path.endswith('/item'):
                return_response = item.list(event, context)
                self.send_response(200)
            elif self.path.endswith('/session'):
                return_response = session.new(event, context)
                self.send_response(200)
            elif self.path.endswith('/status'):
                return_response = status.queue_status(event, context)
                self.send_response(200)
            elif self.path.endswith('/ping'):
                return_response = ping.ping(event, context)
                self.send_response(200)
            else :
                self.send_response(500)
        except Exception:
            traceback.print_exc()       
            self.send_response(500)

        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(return_response["body"].encode())
        
    def do_POST(self):
        return_response = response.failure("Error or unsupported operations")
        event = {"Session" : self.headers['Session'], "Authorization" : self.headers['Authorization']}
        context = {}
        try:
            if self.path.endswith('/order'):
                return_response = order.purchase(event, context)
                self.send_response(200)
            else :
                self.send_response(500)
        except Exception:
            traceback.print_exc()       
            self.send_response(500)

        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(return_response["body"].encode())

httpd = HTTPServer(('localhost', 8080), LocalServerRouter)
httpd.serve_forever()