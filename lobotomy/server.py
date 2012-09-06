import socket
from threading import Thread

from lobotomy import protocol

class LoBotomyServer:
	"""
	Server for a LoBotomy game.
	"""

	def __init__(self, host = '', port = sum(map(ord, 'LoBotomyServer'))):
		self.host = host
		self.port = port

		self.players = []

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
				client = Player(self, client)
				self.players.append(client)
				client.start()
			except:
				pass

class Player(Thread):
	"""
	Class modeling a player, handling messages from and to a client.
	"""

	def __init__(self, server, sock):
		# call the constructor of Thread
		super().__init__(self)

		# indicate being a daemon thread
		self.daemon = True

		self._server = server
		self._sock = sock
		self._shutdown = False

		self._handlers = {
			'join': self.handle_join,
			'spawn': self.handle_spawn,
			'move': self.handle_move,
			'fire': self.handle_fire,
			'scan': self.handle_scan,
		}

	def run(self):
		try:
			# read lines from the socket
			for line in self._sock.makefile():
				# split line on whitespace
				parts = line.split()
				# first word is the command
				command = parts[0]
				# remainder are arguments
				arguments = parts[1:]
				# parse arguments into their corresponding values
				arguments = protocol.PARSERS[command](arguments)[1:]

				# reaching this point, arguments have been successfully parsed (not validated)

				# handle command
				self._handlers[command](*arguments)
		except KeyError as e:
			pass
		except ValueError as e:
			pass
		except Exception as e:
			if not self._shutdown:
				# error occurred during regular operations
				# TODO: log error
				self.shutdown()

	def send(self, *arguments):
		# send all data separated by spaces, terminated by a newline
		self._sock.sendall(' '.join(arguments) + '\n')

	def shutdown(self):
		# indicate a shutdown was
		self._shutdown = True

		# close socket
		self._sock.shutdown()
		self._sock.close()

		# remove self from the server's player list
		# XXX: should this be here, or should something like server.leave(self) be called?
		self.server.players.remove(self)
