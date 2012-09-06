# Make sure flake8 ignores this file: flake8: noqa
# current protocol version
VERSION = 0

# predefine error codes
# TODO: store error codes in constants
ERRORS = {
	101: 'move impossible, not enough energy',
	102: 'fire impossible, not enough energy',
	103: 'scan impossible, not enough energy',
	104: 'action impossible, you are dead',

	201: 'name taken, choose another one',
	202: 'invalid state for command',

	301: 'unrecognized or unsupported command',
	302: 'invalid command',
}

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

# welcome command, format: welcome <version> <energy> <charge> <turn_duration> <turns_left>
welcome = command('welcome', int, float, float, int, int)

# spawn command, format: spawn
spawn = command('spawn')

# begin command, format: begin <turn_number> <energy>
begin = command('begin', int, float)

# move command, format: move <angle> <distance>
move = command('move', float, float)

# fire command, format: fire <angle> <distance> <radius> <yield>
fire = command('fire', float, float, float, float)

# scan command, format: scan <radius>
scan = command('scan', float)

# end command, format: end
end = command('end')

# hit command, format: hit <name> <epicenter_angle> <yield>
hit = command('hit', str, float, float)

# death command, format: death <turns>
death = command('death', int)

# detect command, format: detect <name> <angle> <distance> <energy>
detect = command('detect', str, float, float, float)

# error command, format: error <error_number> <explanation>
error = command('error', int, str)

def parse_msg(msg):
	'''
	Parser helper function. Provide this with a message directly from the
	socket and it will parse it using the correct function, returning
	a dictionary containing parameters for the given protocol message,
	including the message name
	'''
	try:
		chunks = msg.split(' ')
		return PARSERS[chunks[0]](msg)
	except:
		return None
