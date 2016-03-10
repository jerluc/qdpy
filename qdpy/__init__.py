from IPython.core.autocall import ExitAutocall
from qdpy.ctx.module import CodeNamespace, AppendingDict
from qdpy.peer.server import start_server, stop_server, join_group, leave_group, list_peers


class CleanShutdown(ExitAutocall):
    def __call__(self):
        unload_ipython_extension(self._ip) 
        super(CleanShutdown, self).__call__()


def load_ipython_extension(ipython):
    # TODO: Is there a cleaner way to do this?
    ipython.user_ns['exit'] = ipython.user_ns['quit'] = CleanShutdown()
    global t
    t = start_server(ipython)
    ipython.register_magic_function(join_group, magic_kind='line')
    ipython.register_magic_function(leave_group, magic_kind='line')
    ipython.register_magic_function(list_peers, magic_kind='line')
    
    
def unload_ipython_extension(ipython):
    stop_server()
    global t; t.join()

