import signal

from lobotomy.server import LoBotomyServer

# create a server object
server = LoBotomyServer()

# define a shutdown handler
def shutdown(signal, frame):
	logging.info("caught SIGINT, requesting shutdown")
	server.shutdown()

# add a signal before serving
signal.signal(signal.SIGINT, shutdown)

# setup simple logging to print messages from server
import logging
logging.basicConfig(level = 'DEBUG')

# start the server
server.serve_forever()
