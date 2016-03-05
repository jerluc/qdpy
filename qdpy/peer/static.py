STATIC_GROUPS = {
    'compute': [
        
    ]
}

class Group(object):
    def __init__(self, identifier):
        assert identifier, 'Groups must have a non-empty identifier'
        self.identifier = identifier

    def join(self):
        pass
