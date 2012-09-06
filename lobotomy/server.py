import socket
from threading import Thread

from lobotomy import LoBotomyException, protocol
from lobotomy.util import enum

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
				Player(self, client).start()
			except:
				pass

# enumerate possible player states
PlayerState = enum('VOID', 'WAITING', 'ACTING', 'DEAD')

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

		self.state = PlayerState.VOID

		self.move = None
		self.fire = None
		self.scan = None

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
				arguments = protocol.PARSERS[command](arguments)
				# remove the command, handles have no such argument
				del arguments['command']

				# reaching this point, arguments have been successfully parsed (not validated)

				# handle command
				self._handlers[command](**arguments)
		except LoBotomyException as e:
			self.send_error(e.errno)
		except KeyError as e:
			self.send_error(301)
		except ValueError as e:
			self.send_error(302)
		except Exception as e:
			if not self._shutdown:
				# error occurred during regular operations
				# TODO: log error
				self.shutdown()

	def signal_begin(self, turn_number, energy):
		self.state = PlayerState.ACTING

		# reset action requests
		self.move = None
		self.fire = None
		self.scan = None

		self.send(protocol.begin(turn_number, energy).values())

	def signal_end(self):
		self.state = PlayerState.WAITING
		self.send(protocol.end().values())

	def signal_death(self, turns):
		self.state = PlayerState.DEAD
		self.send(protocol.death(turns).values())

	def handle_join(self, name):
		if self.state is not PlayerState.WAITING:
			raise LoBotomyException(202)

		self.state = PlayerState.DEAD

	def handle_spawn(self):
		if self.state is not PlayerState.DEAD:
			raise LoBotomyException(202)

		self.state = PlayerState.WAITING

	def handle_move(self, direction, distance):
		if self.state is not PlayerState.ACTING:
			raise LoBotomyException(202)

		# TODO: check validity
		self.move = (direction, distance)

	def handle_fire(self, direction, distance, radius, charge):
		if self.state is not PlayerState.ACTING:
			raise LoBotomyException(202)

		# TODO: check validity
		self.fire = (direction, distance, radius, charge)

	def handle_scan(self, radius):
		if self.state is not PlayerState.ACTING:
			raise LoBotomyException(202)

		# TODO: check validity
		self.scan = (radius,)

	def send_error(self, error):
		self.send(protocol.error(error, protocol.ERRORS[error]))

	def send(self, *arguments):
		# send all data as strings separated by spaces, terminated by a newline
		self._sock.sendall(' '.join(map(str, arguments)) + '\n')

	def shutdown(self):
		# indicate a shutdown was
		self._shutdown = True

		# close socket
		self._sock.shutdown()
		self._sock.close()

		# TODO: indicate shutdown at server
