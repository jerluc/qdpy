import tornado.ioloop
import tornado.iostream
from tornado import gen
import socket
import uuid
from urlparse import urlsplit


_GROUP_ADDR = ('239.192.1.100', 50007)
_ADVERTISE_INTERVAL = 1000 * 2
_1KB = 1024 * 1


def gethostname():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 53))  # connecting to a UDP address doesn't send packets
    return s.getsockname()[0]


def parse_payload(data):
    uri = urlsplit(data)
    if uri.scheme != 'qdpy':
        return None

    peer_id = uri.username
    peer_group = uri.path[1:]
    peer_ip = uri.hostname
    peer_port = uri.port
    return peer_group, peer_id, peer_ip, int(peer_port)


def create_payload(peer_group, peer_id, peer_ip, peer_port):
    return 'qdpy://%s@%s:%d/%s' % (peer_id, peer_ip, peer_port, peer_group)


class Peer(object):
    def __init__(self, addr, ioloop=None, groups=[]):
        self.id = str(uuid.uuid4())
        self.groups = groups[:]
        self.peers = {}
        self.addr = addr
        self.ioloop = ioloop if ioloop is not None else tornado.ioloop.IOLoop.instance()
        self._socket = None

    def join(self, group):
        self.ioloop.add_callback(self.groups.append, group)

    def leave(self, group):
        self.ioloop.add_callback(self.groups.remove, group)

    @property
    def socket(self):
        if not self._socket:
            host, port = _GROUP_ADDR
	    # Create the socket
	    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	    s.setblocking(False)

	    # Set some options to make it multicast-friendly
	    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
	    s.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 20)
	    s.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)

	    s.bind(('', port))

	    # Set some more multicast options
	    intf = socket.gethostbyname(socket.gethostname())
	    s.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(intf))
	    s.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(host) + socket.inet_aton(intf))

            self._socket = s
        return self._socket

    def start(self):
	self.ioloop.add_handler(self.socket, self.on_peer, tornado.ioloop.IOLoop.READ)
        self._advertiser = tornado.ioloop.PeriodicCallback(self.advertise, _ADVERTISE_INTERVAL)
        self._advertiser.start()

    def on_peer(self, _not, _used):
        data, _ = self.socket.recvfrom(_1KB)
        peer_group, peer_id, peer_ip, peer_port = parse_payload(data)
        if peer_group in self.groups and peer_id != self.id:
            self.peers[peer_id] = (peer_ip, peer_port)

    def advertise(self):
        for group in self.groups:
            host, port = self.addr
	    data = create_payload(group, self.id, host, port)
	    self.socket.sendto(data, _GROUP_ADDR)