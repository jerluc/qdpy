import json
import threading
import tornado.ioloop
import tornado.netutil
import tornado.web
from tornado.httpclient import HTTPClient
from tornado.httpserver import HTTPServer
from qdpy.marshal import loads, dumps
from qdpy.peer.discovery import *


_CODE_BROADCAST_INTERVAL = 1000 * 1
_KRAKEN = threading.Semaphore(0)
_ENV = {
  'ipython': None,
  'initial_keys': [],
  'peer': None
}


def filter_keys(items):
    return filter(lambda i: i[0] not in _ENV['initial_keys'] and not i[0].startswith('_'), items)


def dump_ns():
    code = {k: v for k, v in filter_keys(_ENV['ipython'].user_ns.iteritems())}
    code = {k: dumps(v) for k, v in code.iteritems()}
    return json.dumps(code)


class CodeNamespaceHandler(tornado.web.RequestHandler):
    def put(self):
        code = json.loads(self.request.body)
        code = {k: loads(v) for k, v in filter_keys(code.iteritems())}
        # TODO: Convert to use some more sophisticated dictionary
        # like an append-only or log-ephemeral value storage mechanism
        # much like what Rift hopes to accomplish with time/space/context
        _ENV['ipython'].user_ns.update(code)


def output(msg, *args):
    _ENV['ipython'].write((msg % args) + '\n')


def start_server(ipython, groups=[]):
    global _ENV
    _ENV['ipython'] = ipython
    _ENV['initial_keys'] = ipython.user_ns.keys()
    t = threading.Thread(target=_start_server, args=(groups,))
    t.daemon = True
    t.start()
    _KRAKEN.acquire()
    peer = _ENV['peer']
    host, port = peer.addr
    output('Started QDPY code server @ %s:%d', host, port)
    output('Will join network groups as peer [%s]', peer.id)
    return t

def on_event(event_type, **kwargs):
    if event_type == JOIN_GROUP:
        output('Joined group [%s]', kwargs['group'])
    if event_type == LEAVE_GROUP:
        output('Left group [%s]', kwargs['group'])
    if event_type == NEW_PEER:
        output('Added peer [%s]', kwargs['id'])
    if event_type == REMOVE_PEER:
        output('Removed peer [%s]', kwargs['id'])

def _start_server(groups):
    global _ENV
    app = tornado.web.Application([
	(r'/code', CodeNamespaceHandler),
    ])
    server = tornado.httpserver.HTTPServer(app)
    sockets = tornado.netutil.bind_sockets(0, '')
    server.add_sockets(sockets)
    socket = filter(lambda s: s.getsockname()[0] == '0.0.0.0', sockets)[0]
    host = gethostname()
    port = socket.getsockname()[1]
    peer = Peer((host, port), groups=groups, event_handler=on_event)
    _ENV['peer'] = peer
    peer.start()
    updater = tornado.ioloop.PeriodicCallback(update_ns, _CODE_BROADCAST_INTERVAL)
    updater.start()
    _KRAKEN.release()
    tornado.ioloop.IOLoop.instance().start()


def stop_server():
    tornado.ioloop.IOLoop.instance().stop()


def update_ns():
    code = dump_ns()
    # TODO: Scope each code update to the group somehow
    for peer_id, peer in _ENV['peer'].get_peers().iteritems():
        endpoint = 'http://%s:%d/code' % peer['addr']
        try:
            HTTPClient().fetch(endpoint, method='PUT', body=code)
        except:
            # TODO: For now, we don't do anything anymore, but maybe that call to `unhealthy_peer`
            # is still warranted?
            pass


def join_group(group):
    _ENV['ipython']
    _ENV['peer'].join(group)


def leave_group(group):
    _ENV['peer'].leave(group)


def list_peers(_):
    for peer_id, peer in _ENV['peer'].get_peers().iteritems():
        output('[%s] => %s:%d', peer_id, peer['addr'][0], peer['addr'][1])


