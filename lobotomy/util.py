# global utilities

def enum(**enums):
	"""
	Creates an enumeration with integer values.
	"""
	return type('Enum', (), enums)
