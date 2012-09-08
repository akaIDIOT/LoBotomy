# global utilities

import math

def enum(*values):
	"""
	Creates an enumeration with integer values.
	"""
	enums = dict(zip(values, range(len(values))))
	return type('Enum', (), enums)

def distance(a, b):
	"""
	Calculates the distance between two points encoded as (x, y).
	"""
	ax, ay = a
	bx, by = b

	dx = ax - bx
	dy = ay - by

	return math.sqrt(dx ** 2 + dy ** 2)
