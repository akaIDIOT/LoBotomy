# make sure flake8 ignores this file: flake8: noqa

# store network details
class host:
	# network address to bind to
	address = ''
	# port to listen on (1452)
	port = sum(map(ord, 'LoBotomyServer'))

# store general game settings
class game:
	# turn length, time in ms the server will wait before executing a turn
	turn_duration = 5000

# store player settings
class player:
	# maximum and starting energy for players
	max_energy = 1.0
	# amount of energy that is recharged at the end of each turn
	turn_charge = 0.2

