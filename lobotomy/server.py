# make sure flake8 ignores this file: flake8: noqa

import logging
import random
import socket
from threading import Thread
import time

from lobotomy import config, game, LoBotomyException, protocol, util
from lobotomy.quadtree import Point, QuadTree
from lobotomy.util import enum

class LoBotomyServer:
	"""
	Server for a LoBotomy game.
	"""

	def __init__(self, field_dimensions = config.game.field_dimensions, host = config.host.address, port = config.host.port):
		# create battlefield
		self.width, self.height = field_dimensions
		self.field = QuadTree((0, 0, self.width, self.height))

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
						# not an expected exception
						logging.critical('unexpected network error, shutting down server: %s', str(e))
		except Exception as e:
			logging.critical('unexpected error: %s', str(e))

		# TODO: close all client threads (not all present in self._players)

	def run_game(self):
		logging.info('game loop started')
		while not self._shutdown:
			# increment internal turn counter
			self.turn_number += 1

			# FIXME: iterating over ALL the players time and time again must be slow

			# send all alive players a new turn command
			for player in self._in_game:
				player.energy = min(config.player.max_energy + config.player.turn_charge, 1.0)
				player.send(protocol.begin(self.turn_number, player.energy).values())

			# decrement wait counters for dead players
			for player in filter(lambda p: p.state is PlayerState.DEAD, self._players.values()):
				player.dead_turns -= 1

			# wait the configured amount of time for players to submit commands
			time.sleep(config.game.turn_duration / 1000)

			# execute all requested move actions
			self.execute_moves(filter(lambda p: p.move_action is not None, self._in_game))

			# execute all requested fire actions
			self.execute_fires(filter(lambda p: p.fire_action is not None, self._in_game), self._in_game)

			# execute all requested scan actions
			self.execute_scans(filter(lambda p: p.scan_action is not None, self._in_game), self._in_game)

			# remove all dead players from the battlefield
			for player in filter(lambda p: p.state is PlayerState.DEAD, self._in_game):
				self.field.remove(player)

			# send all players the end turn command
			for player in self._in_game:
				player.signal_end()

	def execute_moves(players):
		for player in players:
			# unpack required inforation
			angle, distance = player.move_action
			# calculate new values
			x = (player.x + cos(angle) * distance) % self.width
			y = (player.y + sin(angle) * distance) % self.height
			# subtract energy cost
			player.energy -= game.move_cost(distance)
			if player.energy <= 0.0:
				# signal player is dead
				player.signal_death(config.player.dead_turns)
			else:
				# move player on the battlefield
				player.move((x, y))

	def execute_fires(players, subjects):
		# TODO: account for world wrapping
		for player in players:
			# unpack required information
			(angle, distance, radius, charge) = player.fire
			# calculate the epicenter of the blast
			epicenter = (
				(player.x + cos(angle) * distance) % self.width,
				(player.y + sin(angle) * distance) % self.height
			)

			# TODO: subtract energy cost (and signal death if it proved fatal)

			for subject in subjects:
				# calculate distance to epicenter for all subjects, signal hit if ... hit
				if util.distance(epicenter, (subjectx, subject.y)) <= radius:
					subject.signal_hit(
						player.name,
						util.angle((subject.x, subject.y), epicenter),
						charge
					)

	def execute_scans(players, subjects):
		# TODO: account for world wrapping
		for player in players:
			(radius,) = player.scan

			# TODO: subtract energy cost (and signal death if it proved fatal)

			for subject in subjects:
				# calculate distance to all subjects, signal detect if within scan
				distance = util.distance((player.x, player.y), (subject.x, subject.y))
				if distance <= radius:
					player.signal_detect(
					        subject.name,
					        util.angle((player.x, player.y), (subject.x, subject.y)),
					        distance,
					        subject.energy
					)

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

	def unregister(self, name, player):
		# remove player from game if the player is in it
		if player in self._in_game:
			self._in_game.remove(player)

		# remove player from online players
		del self._players[name]
		# TODO: include player host
		logging.info('player %s left', name)

	def request_spawn(self, player):
		if player.dead_turns > 0:
			raise LoBotomyException(104)

		# set player start values
		player.energy = config.player.max_energy
		player.x, player.y = (random.random() * self.width, random.random() * self.height)
		self.field.add(player)

		self._in_game.append(player)

	def shutdown(self):
		# avoid double shutdown
		if self._shutdown:
			return

		# request shutdown in main loop
		self._shutdown = True
		logging.info('shutting down server')
		# close the socket real good
		try:
			self._ssock.shutdown(socket.SHUT_RDWR)
			self._ssock.close()
		except:
			# ignore at this point
			pass

# enumerate possible player states
PlayerState = enum('VOID', 'WAITING', 'ACTING', 'DEAD')

class Player(Thread, Point):
	"""
	Class modeling a player, handling messages from and to a client.

	TODO: queue signals, just just before end
	"""

	def __init__(self, server, sock):
		# call the constructor of Thread
		super(Thread, self).__init__()
		# call the constructor of Point
		super(Point, self).__init__(None, None)

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
		self.move_action = None
		self.fire_action = None
		self.scan_action = None

		# game state variables
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
		self.move_action = None
		self.fire_action = None
		self.scan_action = None

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
		# check state
		if self.state is not PlayerState.ACTING:
			raise LoBotomyException(202)

		# check action validity
		if game.move_cost(distance) > config.player.max_energy:
			raise LoBotomyException(101)

		self.move_action = (direction, distance)

	def handle_fire(self, direction, distance, radius, charge):
		# check state
		if self.state is not PlayerState.ACTING:
			raise LoBotomyException(202)

		# check action validity
		if game.fire_cost(distance, radius, charge) > config.player.max_energy:
			raise LoBotomyException(102)

		self.fire = (direction, distance, radius, charge)

	def handle_scan(self, radius):
		# check state
		if self.state is not PlayerState.ACTING:
			raise LoBotomyException(202)

		# check action validity
		if game.scan_cost(radius) > config.player.max_energy:
			raise LoBotomyException(103)

		self.scan_action = (radius,)

	def send_error(self, error):
		logging.debug('client caused error %d', error)
		self.send(protocol.error(error, protocol.ERRORS[error]).values())

	def send(self, command):
		# send all data as strings separated by spaces, terminated by a newline
		try:
			self._sock.sendall(bytes(' '.join(map(str, command)) + '\n', 'utf-8'))
		except Exception as e:
			logging.error('unexpected network error, client will crash: %s', str(e))
			self.shutdown()

	def shutdown(self):
		# avoid closing and unregistering twice
		if self._shutdown:
			return

		# indicate a shutdown was requested
		self._shutdown = True

		logging.info('shutting down client')
		# close socket
		try:
			self._sock.shutdown(socket.SHUT_RDWR)
			self._sock.close()
		except:
			# ignore at this point
			pass

		# unregister ourselves from the server if we were registered
		# TODO: find better way of determining this
		if not self.name.startswith('Thread-'):
			self._server.unregister(self.name, self)
