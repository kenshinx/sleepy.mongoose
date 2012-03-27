from wsgiref.simple_server import make_server
from BaseHTTPServer import BaseHTTPRequestHandler
from httpd import MongoHTTPRequest
from handlers import MongoHandler
import urlparse
import config

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
        self.body = []
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
        
    def _parse_call(self, uri):
        """ 
        this turns a uri like: /foo/bar/_query into properties: using the db 
        foo, the collection bar, executing a query.

        returns the database, collection, and action
        """
        parts = uri.split('/')

        # operations always start with _
        if parts[-1][0] != '_':
            return (None, None, None)

        if len(parts) == 1:
            return ("admin", None, parts[0])
        elif len(parts) == 2:
            return (parts[0], None, parts[1])
        else:
            return (parts[0], ".".join(parts[1:-1]), parts[-1])


    def call_handler(self, uri, args):
        """ execute something """

        (db, collection, func_name) = self._parse_call(uri)
        if db == None or func_name == None:
            self.send_error(404, 'Script Not Found: '+uri)
            return

        name = None
        if "name" in args:
            if type(args).__name__ == "dict":
                name = args["name"][0]
            else:
                name = args.getvalue("name")
        print db, collection, func_name
        print name
        self.jsonp_callback = None
        if "callback" in args:
            if type(args).__name__ == "dict":
                self.jsonp_callback = args["callback"][0]
            else:
                self.jsonp_callback = args.getvalue("callback")
                
        MongoHandler.mh = MongoHandler(config.mongos)
                
        func = getattr(MongoHandler.mh, func_name, None)
        if callable(func):
            self.send_response(200)
            self.send_header('Content-type', MongoHTTPRequest.mimetypes['json'])

            if self.jsonp_callback:
                func(args, self.prependJSONPCallback, name = name, db = db, collection = collection)
            else:
                func(args, self._catch_response, name = name, db = db, collection = collection)

            return
        else:
            self.send_error(404, 'Script Not Found: '+uri)
            return            
        
    def prependJSONPCallback(self, str):
        jsonp_output = '%s(' % self.jsonp_callback + str + ')'
        self.send_response(200,jsonp_output)
    
    def do_GET(self):
        uri, args, type = self.process_uri(self.method)
        
        if len(type) != 0:
            if type in MongoHTTPRequest.mimetypes and os.path.exists(MongoHTTPRequest.docroot+uri):

                fh = open(MongoHTTPRequest.docroot+uri, 'r')

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
        if (message is None) :
            message = self.responses[code][0]
           
        self.status = "%d %s" %(code,self.responses[code][0])
        self.body.append(message)
        
    def send_error(self,code, message=None):
        self.status = "%d %s" %(code,self.responses[code][0])
        self.body.append(message)
        
    
    def send_header(self,key,val):
        self.headers.setdefault(key,val)
        
    def _catch_response(self,message):
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
    webbrowser.open('http://localhost:27080/kenshin/urls/_find')
    #httpd.serve_forever()
    httpd.handle_request()
 