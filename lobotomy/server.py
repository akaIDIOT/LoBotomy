# make sure flake8 ignores this file: flake8: noqa

import logging
import socket
from threading import Thread
import time

from lobotomy import config, LoBotomyException, protocol
from lobotomy.util import enum

class LoBotomyServer:
	"""
	Server for a LoBotomy game.
	"""

	def __init__(self, host = config.host.address, port = config.host.port):
		self.host = host
		self.port = port

		# track online players by name
		self._players = {}
		# track players in game
		self._in_game = []

		self.turn_number = 0

	def serve_forever(self):
		logging.debug('preparing network setup for serving at "%s:%d"', self.host, self.port)
		self._ssock = socket.socket()
		try:
			# bind a socket to the specified host and port
			self._ssock.bind((self.host, self.port))
			# make the socket listen for new connections
			self._ssock.listen(5)
			logging.info('succesfully bound to %s:%d, listening for clients', self.host, self.port)


			self._shutdown = False

			# start a game
			Thread(name = 'game loop', target = self.run_game).start()

			# loop as long as a shutdown was not requested
			while not self._shutdown:
				try:
					# accept a connection from a client
					client, address = self._ssock.accept()
					logging.info('client from %s connected', address[0])
					Player(self, client).start()
				except Exception as e:
					if not self._shutdown:
						# no an expected exception
						logging.critical('unexpected network error, shutting down server: %s', str(e))
		except Exception as e:
			logging.critical('unexpected error: %s', str(e))

		# TODO: close all client threads (not all present in self._players())

	def run_game(self):
		logging.info('game loop started')
		while not self._shutdown:
			# TODO: run a turn
			time.sleep(config.game.turn_duration / 1000)
			logging.debug('slept like a baby...')

	def register(self, name, player):
		if name in self._players:
			# TODO: include player host
			logging.debug('player tried to register as %s, name is in use', name)
			raise LoBotomyException(201)

		# register player
		self._players[name] = player
		# send welcome message
		player.send(protocol.welcome(
			protocol.VERSION,
			config.player.max_energy,
			config.player.turn_charge,
			config.game.turn_duration,
			-1
		).values())
		# TODO: include player host
		logging.info('player %s joined', name)

	def unregister(self, name):
		del self._players[name]
		# TODO: include player host
		logging.info('player %s left', name)

	def request_spawn(self, player):
		if player.dead_turns > 0:
			raise LoBotomyException(104)

		# TODO: perform spawn

	def shutdown(self):
		# request shutdown in main loop
		self._shutdown = True
		logging.info('shutting down server')
		# close the socket real good
		self._ssock.shutdown(socket.SHUT_RDWR)
		self._ssock.close()

# enumerate possible player states
PlayerState = enum('VOID', 'WAITING', 'ACTING', 'DEAD')

class Player(Thread):
	"""
	Class modeling a player, handling messages from and to a client.

	TODO: queue signals, just just before end
	"""

	def __init__(self, server, sock):
		# call the constructor of Thread
		super().__init__()

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

		# actions requested by the client
		self.move = None
		self.fire = None
		self.scan = None

		# game state variables
		self.location = (None, None)
		self.energy = 0.0
		self.dead_turns = 0

	def run(self):
		try:
			# read lines from the socket
			for line in self._sock.makefile():
				try:
					# split line on whitespace
					parts = line.split()
					# first word is the command
					command = parts[0]
					# remainder are arguments
					arguments = parts[1:]
					# parse arguments into their corresponding values
					arguments = protocol.PARSERS[command](*arguments)
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
				logging.error('unexpected network error, client will crash: %s', str(e))
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

	def signal_hit(self, name, angle, charge):
		self.send(protocol.fire(name, angle, charge).values())

	def signal_death(self, turns):
		self.state = PlayerState.DEAD
		self.send(protocol.death(turns).values())

	def signal_detect(self, name, angle, distance, energy):
		self.send(protocol.detect(name, angle, distance, energy).values())

	def handle_join(self, name):
		if self.state is not PlayerState.VOID:
			raise LoBotomyException(202)

		try:
			# attempt to register client with server
			self._server.register(name, self)
			# no exception, we're good (real good!)
			self.name = name
			self.state = PlayerState.DEAD
		except LoBotomyError as e:
			self.send_error(e.errno)

	def handle_spawn(self):
		if self.state is not PlayerState.DEAD:
			raise LoBotomyException(202)

		try:
			self._server.request_spawn(self)
			self.state = PlayerState.WAITING
		except LoBotomyError as e:
			self.send_error(e.errno)

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
		logging.debug('client caused error %d', error)
		self.send(protocol.error(error, protocol.ERRORS[error]).values())

	def send(self, command):
		# send all data as strings separated by spaces, terminated by a newline
		self._sock.sendall(bytes(' '.join(map(str, command)) + '\n', 'utf-8'))

	def shutdown(self):
		# indicate a shutdown was
		self._shutdown = True

		logging.info('shutting down client')
		# close socket
		self._sock.shutdown(socket.SHUT_RDWR)
		self._sock.close()

		# TODO: indicate shutdown at server

