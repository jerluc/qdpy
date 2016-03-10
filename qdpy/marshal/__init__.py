from dill import dumps as dumpz, loads as loadz
from base64 import b64encode as encode, b64decode as decode


def loads(data):
    return loadz(decode(data))

def dumps(data):
    return encode(dumpz(data))
