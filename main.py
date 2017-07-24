#!/usr/bin/env python

"""
TESTING
-------

$ python main.py

curl "http://localhost:8080/"
curl "http://localhost:8080/users"
# CREAR
curl -d "email=micorreo@empresa.com&text1=John&text2=Snow&text3=avlostronos" http://localhost:8080/users
# ACTUALIZAR
curl -X PUT -d '{"firstname": "John"}' "http://localhost:8080/user/1"
curl -X PUT -d '{"lastname": "Lennon"}' "http://localhost:8080/user/2"
curl "http://localhost:8080/users"
# ELIMINAR
curl -X DELETE "http://localhost:8080/user/2"
curl "http://localhost:8080/users"

"""

import sys, os, re, shutil, json, urllib, sqlobject
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from sqlobject.sqlite import builder
from User import User

reload(sys)
sys.setdefaultencoding('utf8')
res = {}

def to_dict(obj):
    cls = type(obj)
    d = dict((c, getattr(obj, c)) for c in vars(cls) if isinstance(getattr(cls, c), property))
    return d

def get_records(handler):
    users = User.select()
    result = [to_dict(row) for row in users]
    res = json.dumps(result)
    return res


def get_record(handler):
    key = urllib.unquote(handler.path[-1])
    try:
        users = User.select(User.q.id==int(key))
        result = [to_dict(row) for row in users]
        res = json.dumps(result[0])
        return res
    except Exception, e:
        return u'Error'

def set_record(handler):
    key = urllib.unquote(handler.path[-1])
    try:
        user = User.select(User.q.id==int(key))[0]
        if user:
            payload = handler.get_payload()
            if payload.get('email'):
                user.email = payload['email']
            if payload.get('firstname'):
                user.firstname = payload['firstname']
            if payload.get('lastname'):
                user.lastname = payload['lastname']
            if payload.get('address'):
                user.address = payload['address']
            res[key] = "%s %s" % (user.firstname, user.lastname)
            print u"Usuario actualizado!"
            return res[key]
    except Exception, e:
        return u'No se encuentra datos'
    

def post_record(handler):
    request_headers = handler.headers
    content_length = request_headers.getheaders('content-length')
    length = int(content_length[0]) if content_length else 0

    p = handler.rfile.read(length)
    params = dict(item.split("=") for item in p.split("&"))

    try:
        if params.get('email') and params.get('text1') and params.get('text2') and params.get('text3'):
            user = User(email=params['email'],
                    firstname=params['text1'],
                    lastname=params['text2'],
                    address=params['text3'])
            print u"Se creo el usuario %s" % user.firstname
            return json.dumps(params)
    except Exception, e:
        return u'Error en los datos (Email es unico)'

def delete_record(handler):
    key = urllib.unquote(handler.path[-1])
    try:
        user = User.select(User.q.id==int(key))[0]
        User.delete(user.id)
        print u"Usuario eliminado!"
        del res[key]        
        return True
    except Exception, e:
        return u'No se encuentra datos'


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.routes = {
            r'^/$': {'file': 'index.html', 'media_type': 'text/html'},
            r'^/users$': {'GET': get_records, 'POST': post_record, 'media_type': 'application/json'},
            r'^/user/(?P<id>\d+)': {'GET': get_record,
                         'PUT': set_record,
                         'DELETE': delete_record,
                         'media_type': 'application/json'}}

        return BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def do_HEAD(self):
        self.handle_method('HEAD')

    def do_GET(self):
        self.handle_method('GET')

    def do_POST(self):
        self.handle_method('POST')

    def do_PUT(self):
        self.handle_method('PUT')

    def do_DELETE(self):
        self.handle_method('DELETE')

    def get_payload(self):
        payload_len = int(self.headers.getheader('content-length', 0))
        payload = self.rfile.read(payload_len)
        payload = json.loads(payload)
        return payload

    def handle_method(self, method):
        route = self.get_route()

        if route is None:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(u'No se encuentra la ruta\n')
        else:
            if method == 'HEAD':
                self.send_response(200)
                if 'media_type' in route:
                    self.send_header('Content-type', route['media_type'])
                self.end_headers()
            else:
                if 'file' in route:
                    if method == 'GET':
                        try:
                            here = os.path.dirname(os.path.realpath(__file__))
                            f = open(os.path.join(here, route['file']))
                            print f
                            try:
                                self.send_response(200)
                                if 'media_type' in route:
                                    self.send_header('Content-type', route['media_type'])
                                self.end_headers()
                                shutil.copyfileobj(f, self.wfile)
                            finally:
                                f.close()
                        except:
                            self.send_response(404)
                            self.end_headers()
                            self.wfile.write(u'No existe el archivo\n')
                    else:
                        self.send_response(405)
                        self.end_headers()
                        self.wfile.write(u'Solo se recibe GET\n')
                else:
                    if method in route:
                        content = route[method](self)
                        if content is not None:
                            self.send_response(200)
                            if 'media_type' in route:
                                self.send_header('Content-type', route['media_type'])
                            self.end_headers()
                            if method != 'DELETE':
                                self.wfile.write(json.dumps(content))
                        else:
                            self.send_response(404)
                            self.end_headers()
                            self.wfile.write(u'No hay servicio, error 404\n')
                    else:
                        self.send_response(405)
                        self.end_headers()
                        self.wfile.write(method + u' no esta habilitado, error 405\n')

    def get_route(self):
        for path, route in self.routes.iteritems():
            if re.match(path, self.path):
                return route
        return None


def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    server_address = ('', port)
    http_server = server_class(server_address, handler_class)
    print u'Iniciamos el servicio por el puerto :%s...' % port
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        pass
    print u'HTTP server Cerrado'
    http_server.server_close()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
