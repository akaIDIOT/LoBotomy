# store message handlers by their command string
HANDLERS = {}

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
			raise ValueError('malformed argument: ' + str(e))
		except IndexError as e:
			raise ValueError('invalid number of arguments', len(types), len(arguments))

	# map the handler's name to its parser
	HANDLERS[name] = parser

	return parser
