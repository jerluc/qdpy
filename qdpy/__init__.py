import threading
import signal
from IPython.core.autocall import ExitAutocall
from qdpy.ctx.module import CodeNamespace, AppendingDict
from qdpy.peer.server import start_server, stop_server


class CleanShutdown(ExitAutocall):
    def __call__(self):
        unload_ipython_extension(self._ip) 
        super(CleanShutdown, self).__call__()


def load_ipython_extension(ipython):
    ipython.user_ns['exit'] = ipython.user_ns['quit'] = CleanShutdown()
    global t; t = threading.Thread(target=start_server, args=(ipython, 'qdpy')); t.start()
    
    
def unload_ipython_extension(ipython):
    stop_server()
    global t; t.join()

