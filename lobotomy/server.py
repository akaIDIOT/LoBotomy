import socket

class LoBotomyServer:
	"""
	Server for a LoBotomy game.
	"""
	def __init__(self, host = '', port = sum(map(ord, 'LoBotomyServer'))):
		self.host = host
		self.port = port

	def serve_forever(self):
		self._ssock = socket.socket()
		# bind a socket to the specified host and port
		self._ssock.bind((self.host, self.port))
		# make the socket listen for new connections
		self._ssock.listen(5)

		self._shutdown = False

		# loop as long as a shutdown was not requested
		while not self._shutdown:
			try:
				# accept a connection from a client
				client, address = self._ssock.accept()
			except:
				pass
