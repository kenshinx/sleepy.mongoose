from wsgiref.simple_server import make_server
from BaseHTTPServer import BaseHTTPRequestHandler
from httpd import MongoHTTPRequest


class WSGIResponse(object):
    def __init__(self,status=None, headers={},body=None):
        self.body = body
        self.status = status
        self.headers = headers
    
   
    



class WSGIRequest(BaseHTTPRequestHandler):
    def __init__(self,environ):
        if type(environ) is not dict:
            raise TypeError(
                "WSGI environ must be a dict; you passed %r" % (environ,))
        self.environ = environ
        self.method = environ.get("REQUEST_METHOD")
        self.status = ""
        self.body = ""
        self.headers = {}
        
        self.handle_request(self.method)
        
    
    def handle_request(self,method):
        mname = 'do_' + method
        func = getattr(self,mname)
        if callable(func):
            func()
        else:
            self.send_error(400,"Invalid request method") 
        
    def process_uri(self, method):
        if method == "GET":
            (uri, q, args) = self.path.partition('?')
        else:
            uri = self.path
            if 'Content-Type' in self.headers:
                args = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                                        environ={'REQUEST_METHOD':'POST',
                                                 'CONTENT_TYPE':self.headers['Content-Type']})
            else:
                self.send_response(100, "Continue")
                self.send_header('Content-type', MongoHTTPRequest.mimetypes['json'])
                for header in self.response_headers:
                    self.send_header(header[0], header[1])
                self.end_headers()
                self.wfile.write('{"ok" : 0, "errmsg" : "100-continue msgs not handled yet"}')

                return (None, None, None)


        uri = uri.strip('/')
    
        # default "/" to "/index.html"
        if len(uri) == 0:
            uri = "index.html"

        (temp, dot, type) = uri.rpartition('.')
        # if we have a collection name with a dot, don't use that dot for type
        if len(dot) == 0 or uri.find('/') != -1:
            type = ""
        return (uri, args, type)
    
    
    def do_GET(self):
        uri, args, type = self.process_uri(self.method)
        self.send_header('Content-type', MongoHTTPRequest.mimetypes['json'])
        self.send_response(200,"hi kenshin")
     
    
    def do_POST(self):
        pass
    
    
    @property
    def qs(self):
        return self.environ.get('QUERY_STRING')
        
    @property    
    def path(self):
        path = self.environ.get('PATH_INFO')
        if self.qs:
            path += '?' + self.qs
        return path
    
    def send_response(self,code, message=None):
        if message is None:
            message = self.responses[code][0]
           
        self.status = "%d %s" %(code,self.responses[code][0])
        self.body = message
    
    def send_error(self,code, message=None):
        self.status = "%d %s" %(code,self.responses[code][0])
        self.body = message
        
    
    def send_header(self,key,val):
        self.headers.setdefault(key,val)
        
    
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
        return [response.body]
        
app = WSGIMongoAPP()

if __name__ == '__main__':
    httpd = make_server('', 27080, app)
    import webbrowser
    webbrowser.open('http://localhost:27080/kenshin/urls/_find?id=123%name=asdsa')
    #httpd.serve_forever()
 