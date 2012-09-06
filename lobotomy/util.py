# global utilities
def enum(*values):
	"""
	Creates an enumeration with integer values.
	"""
	enums = dict(zip(values, range(len(values))))
	return type('Enum', (), enums)
