import click

from .peer.static import Group

import imp, os.path, sys


def import_(filename):
    path, name = os.path.split(filename)
    name, _ = os.path.splitext(name)
    f, filename, data = imp.find_module(name, [path])
    return imp.load_module('__main__', f, filename, data)


class Finder(object):
    def find_module(self, name, path=None):
        return self

    def __call__(self, *args, **kwargs):
        print('Being called')
        return self

    def __getattr__(self, name):
        print('Get attr %s' % name)
        return self

    def load_module(self, name):
        print('Asked to load module: %s' % name)
        return self


@click.command()
@click.argument('filename')
# TODO Actually implement a CLI
def main(filename):
    group = Group('compute')
    sys.meta_path.append(Finder())
    import_(filename)
