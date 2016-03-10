import json
import tornado.ioloop
import tornado.netutil
import tornado.web
from tornado.httpclient import HTTPClient
from tornado.httpserver import HTTPServer
from qdpy.marshal import loads, dumps
from qdpy.peer.discovery import Peer, gethostname


_env = {
  'ipython': None,
  'initial_keys': [],
  'peer': None
}


def filter_keys(items):
    return filter(lambda i: i[0] not in _env['initial_keys'] and not i[0].startswith('_'), items)


def dump_ns():
    code = {k: v for k, v in filter_keys(_env['ipython'].user_ns.iteritems())}
    code = {k: dumps(v) for k, v in code.iteritems()}
    return json.dumps(code)


class CodeNamespaceHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(dump_ns())
    
    def put(self):
        code = json.loads(self.request.body)
        code = {k: loads(v) for k, v in filter_keys(code.iteritems())}
        _env['ipython'].user_ns.update(code)


def start_server(ipython, group):
    global _env
    _env['ipython'] = ipython
    _env['initial_keys'] = ipython.user_ns.keys()
    app = tornado.web.Application([
	(r'/code', CodeNamespaceHandler),
    ])
    server = tornado.httpserver.HTTPServer(app)
    sockets = tornado.netutil.bind_sockets(0, '')
    server.add_sockets(sockets)
    socket = filter(lambda s: s.getsockname()[0] == '0.0.0.0', sockets)[0]
    host = gethostname()
    port = socket.getsockname()[1]
    peer = Peer((host, port), groups=[group])
    _env['peer'] = peer
    peer.start()
    updater = tornado.ioloop.PeriodicCallback(update_ns, 2000)
    updater.start()
    tornado.ioloop.IOLoop.instance().start()


def stop_server():
    tornado.ioloop.IOLoop.instance().stop()


def update_ns():
    code = dump_ns()
    for peer_id, peer in _env['peer'].peers.iteritems():
        endpoint = 'http://%s:%d/code' % peer
        try:
            HTTPClient().fetch(endpoint, method='PUT', body=code)
        except:
            _env['peer'].remove_peer(peer_id)
