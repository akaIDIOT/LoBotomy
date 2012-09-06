import signal
import sys
from lobotomy import config
from lobotomy.server import LoBotomyServer


# Create a server object
server = LoBotomyServer(config.game['host'], config.game['port'])

# Define a shutdown handler
def shutdown(signal, frame):
	print("Shutting down...")
	server.shutdown()
	#sys.exit(0)

# Add a signal before serving
signal.signal(signal.SIGINT, shutdown)

server.serve_forever()
