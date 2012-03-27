from wsgiref.simple_server import make_server
from BaseHTTPServer import BaseHTTPRequestHandler
from httpd import MongoHTTPRequest
from handlers import MongoHandler
import urlparse
import config
import os

class WSGIResponse(object):
    def __init__(self,status=None, headers={},body=None):
        self.body = body
        self.status = status
        self.headers = headers
    



class WSGIRequest(MongoHTTPRequest):
    
    MongoHandler.mh = MongoHandler(config.mongos)
    
    def __init__(self,environ):
        if type(environ) is not dict:
            raise TypeError(
                "WSGI environ must be a dict; you passed %r" % (environ,))
        self.environ  = environ
        self.status = ""
        self.body = []
        self.headers = {}
        self.setup()
        self.handle_request(self.method)
      
    def setup(self):
        class _FakeSocket:
            pass
        self.rfile = _FakeSocket()
        self.wfile = _FakeSocket()
        self.rfile.write = self.wfile.write = self._hack_write
    
    def handle_request(self,method):
        mname = 'do_' + method
        func = getattr(self,mname)
        if callable(func):
            func()
        else:
            self.send_error(400,"Invalid request method") 
        
    
    def do_GET(self):
        uri, args, type = self.process_uri(self.method)
        if len(type) != 0:
            if type in MongoHTTPRequest.mimetypes and os.path.exists(config.docroot+uri):

                fh = open(config.docroot+uri, 'r')

                self.send_response(200, fh.read())
                self.send_header('Content-type', MongoHTTPRequest.mimetypes[type])
                return

            else:
                self.send_error(404, 'File Not Found: '+uri)

                return

        # make sure args is an array of tuples
        if len(args) != 0:
            args = urlparse.parse_qs(args)
        else:
            args = {}
        self.call_handler(uri, args)
     
    
    def do_POST(self):
        (uri, args, type) = self.process_uri("POST")
        if uri == None:
            return
        self.call_handler(uri, args)
    
    
    @property
    def qs(self):
        return self.environ.get('QUERY_STRING')
        
    @property    
    def path(self):
        path = self.environ.get('PATH_INFO')
        if self.qs:
            path += '?' + self.qs
        return path
    
    @property
    def method(self):
        return self.environ.get("REQUEST_METHOD")

    
    def send_response(self,code, message=None):
        self.status = "%d %s" %(code,self.responses[code][0])
        if message is not None:
            self.body.append(message)
        
    def send_error(self,code, message=None):
        short, long = self.responses[code]
        if message is None:
            message = short
        self.status = "%d %s" %(code,self.responses[code][0])
        self.body.append(message)
        
    def send_header(self,key,val):
        self.headers.setdefault(key,val)
        
    def end_headers(self):
        pass
    
    def _hack_write(self,message):
        self.body.append(message)

    def get_response(self):
        response = WSGIResponse(self.status,self.headers,self.body)
        return response
        

class WSGIMongoAPP(object):
    
    def __call__(self,environ, start_response):

        request = WSGIRequest(environ)
        response = request.get_response()
        status = response.status
        response_headers = [(str(k), str(v)) for k, v in response.headers.items()]
        start_response(status, response_headers)
        return response.body
        
app = WSGIMongoAPP()

if __name__ == '__main__':
    httpd = make_server('', 27080, app)
    import webbrowser
    webbrowser.open('http://localhost:27080/kenshin/domains/_find?count=6318')
    #httpd.serve_forever()
    httpd.handle_request()
 