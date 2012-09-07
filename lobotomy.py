import signal
import sys

from lobotomy import config
from lobotomy.server import LoBotomyServer

# create a server object
server = LoBotomyServer(config.host.address, config.host.port)

# define a shutdown handler
def shutdown(signal, frame):
	print("Shutting down...")
	server.shutdown()
	#sys.exit(0)

# add a signal before serving
signal.signal(signal.SIGINT, shutdown)

# setup simple logging to print messages from server
import logging
logging.basicConfig(level = 'DEBUG')

# start the server
server.serve_forever()

