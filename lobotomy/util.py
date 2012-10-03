# global utilities

import math

def enum(*values):
	"""
	Creates an enumeration with integer values.
	"""
	enums = dict(zip(values, range(len(values))))
	return type('Enum', (), enums)

def angle(a, b):
	"""
	Calculates the angle between point two points encoded as (x, y), as seen
	from the first.
	"""
	ax, ay = a
	bx, by = b

	dx = bx - ax
	dy = by - ay

	return math.atan2(dx, dy) % (2 * math.pi)

def distance(a, b):
	"""
	Calculates the distance between two points encoded as (x, y).
	"""
	ax, ay = a
	bx, by = b

	dx = ax - bx
	dy = ay - by

	return math.sqrt(dx ** 2 + dy ** 2)

def move_wrapped(location, angle, distance, field_bounds):
	"""
	Creates new wrapped locations from location, applying angle and distance
	while wrapping the new location with the provided field bounds.
	"""
	# unpack required values
	x, y = location
	width, height = field_bounds

	# calculate new values
	x = (x + math.cos(angle) * distance) % width
	y = (y + math.sin(angle) * distance) % height

	# return new location
	return (x, y)

def generate_wrapped_bounds(field_bounds, target_bounds):
	"""
	Generates bounds of the form (x1, y1, x2, y2) that together represent the
	total area of target_bounds in field_bounds, assuming it wraps.
	"""
	# start with the target bounds (overlapping with 'non-existent' space is not a problem)
	yield target_bounds

	# unpack and calculate all required values
	fx1, fy1, fx2, fy2 = field_bounds
	f_width = fx2 - fx1
	f_height = fy2 - fy1
	tx1, ty1, tx2, ty2 = target_bounds

	# check all possible edge (harhar) cases
	if tx1 < fx1:
		# target area extends the left of field
		yield (tx1 + f_width, ty1, fx2, ty2) # change left and right x values

		if ty1 < fy1:
			# target area *also* extends the top of field (top right covered in left extension)
			yield (fx1, ty1 + f_height, tx2, fy2) # yield 'bottom left' overlap
			yield (tx1 + f_width, ty1 + f_height, fx2, fy2) # yield 'bottom right' overlap
		elif ty2 > fy2:
			# target area *also* extends the bottom of field (bottom right covered in left extension)
			yield (fx1, fy1, tx2, ty2 - f_height) # yield the 'top left' overlap
			yield (tx1 + f_width, fy1, fx2, ty2 - f_height) # yield the 'top right' overlap

	elif tx2 > fx2:
		# target area extends the right of field
		yield (fx1, ty1, tx2 - f_width, ty2) # change left and right x values

		if ty1 < fy1:
			# target area *also* extends the top of field (top left covered in right extension)
			yield (fx1, ty1 + f_height, tx2 - f_width, fy2) # yield the 'bottom left' overlap
			yield (tx1, ty1 + f_height, tx1, fy2) # yield the 'bottom right' overlap
		elif ty2 > fy2:
			# target area *also* extends the bottom field (bottom left covered in right extension)
			yield (fx1, fy1, tx2 - f_width, ty2 - f_height) # yield the 'top left' overlap
			yield (tx1, fy1, fx2, ty2 - f_height) # yield the 'top right' overlap
	elif ty1 < fy1:
		# target area extends the top of field
		yield (tx1, ty1 + f_height, tx2, fy2) # change top and bottom y values
		# conjunctions with corners handled above

	elif ty2 > fy2:
		# target area extends the bottom of field
		yield (tx1, fy1, tx2, ty2 - f_height) # change top and bottom y values
		# conjunctions with corners handled above

class WrappedRadius:
	"""
	Convenience class to check if a point is within the radius of another
	point in a wrapped field.
	"""

	def __init__(self, point, radius, field_bounds):
		"""
		Creates a new wrapped radius of size radius around point.
		"""
		self.point = point
		self.radius = radius
		self.field_bounds = field_bounds

	def __contains__(self, point):
		"""
		Checks whether the point is in self.point's radius in a wrapped field.
		"""
		# check wrapped distances in all directions (and the regular position for x = 0 and y = 0
		for x in (-1, 0, 1):
			# wrap x value
			wrapped_x = point[0] + x * self.field_bounds[0]
			for y in (-1, 0, 1):
				# wrap y value
				wrapped_y = point[1] + y * self.field_bounds[1]
				if distance(self.point, (wrapped_x, wrapped_y)) <= self.radius:
					# if current wrap is within radius, point is in wrapped radius
					return (wrapped_x, wrapped_y)

		# not within any wrapped radius
		return False
