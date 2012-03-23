from wsgiref.simple_server import make_server
from httpd import MongoHTTPRequest


class WSGIResponse(object):
    def __init__(self,status,headers):
        self.status = status
        self.headers = headers
    
   
    



class WSGIRequest(MongoHTTPRequest):
    def __init__(self,environ):
        if type(environ) is not dict:
            raise TypeError(
                "WSGI environ must be a dict; you passed %r" % (environ,))
        self.environ = environ
        self.method = environ.get("REQUEST_METHOD")
        self.handle_request(self.method)
        
    
    def handle_request(self,method):
        mname = 'do_' + method
        func = getattr(self,mname)
        func()
    
        
    
    def do_GET(self):
        uri, args, type = self.process_uri(self.method)
        print uri
        print args
        print type
    
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
        
    
    def get_response(self):
        response = WSGIResponse("200 ok",\
                                {'Content-Type':MongoHTTPRequest.mimetypes['json']})
        return response
        

class WSGIMongoAPP(object):
    
    def __call__(self,environ, start_response):

        request = WSGIRequest(environ)
        response = request.get_response()
        status = response.status
        response_headers = [(str(k), str(v)) for k, v in response.headers.items()]
        start_response(status, response_headers)
        return ["hi!"]
        
app = WSGIMongoAPP()

if __name__ == '__main__':
    httpd = make_server('', 27080, app)
    import webbrowser
    webbrowser.open('http://localhost:27080/kenshin/urls/_find?id=123%name=asdsa')
    httpd.handle_request()
 