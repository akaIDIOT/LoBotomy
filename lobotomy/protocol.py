# store message parsers by their command string
PARSERS = {}

def command(name, *types):
	"""
	Creates a command parser for a named command requiring the provided types
	as arguments.
	"""

	def parser(*arguments):
		try:
			# create a list of the command's name and all the arguments
			# coerced to their respective types
			return [name] + [types[i](arguments[i]) for i in range(len(types))]
		except ValueError as e:
			raise ValueError('malformed argument', str(e))
		except IndexError as e:
			raise ValueError('invalid number of arguments', len(types), len(arguments))

	# map the handler's name to its parser
	PARSERS[name] = parser

	return parser

# join command, format: join <name>
join = command('join', str)

# turn command, format: turn <turn_number> <energy>
turn = command('turn', int, float)

# move command, format: move <angle> <distance>
move = command('move', float, float)

# fire command, format: fire <angle> <distance> <radius>
fire = command('fire', float, float, float)

# scan command, format: scan <radius>
scan = command('scan', float)

# hit command, format: hit <name> <energy>
hit = command('hit', str, float)

# detect command, format: detect <name> <angle> <distance>
detect = command('detect', str, float, float)

# error command, format: error <error_number> <explanation>
error = command('error', int, str)
