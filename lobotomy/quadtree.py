# quadtree spatial index structure

class QuadTree:
	"""
	Quadtree index, spanning particular dimensions.

	The quadtree is a tree structure with 1 to 4 leaves or exactly 4 branches
	on every level, automatically splitting and discarding regions when
	occupation reaches certain thresholds.

	The quadtree is intended for finding entries (points) in a certain
	bounding rectangle.

	Quadtree entries (points) are made aware of their location in the tree, so
	they can be moved by walking the tree to their new location.
	"""

	def __init__(self, dimensions, *points)
		"""
		Creates a new QuadTree spanning the given dimensions, containing the
		specified points.
		"""
		self.root = Region(dimensions)

		for point in points:
			self.add(point)

	def add(self, point):
		pass

class Region:
	"""
	Index region withing a QuadTree, containing either child regions or leaves
	(points). Contains a reference back to its parent, so the tree of regions
	can be traversed in both directions.
	"""

	def __init__(self, dimensions, parent = None, *points):
		"""
		Creates a new Region spanning the given dimensions.
		"""
		self.dimensions = dimensions
		self.parent = parent
		self.children = []
		self.points = points

	def __len__(self):
		# TODO: make this recursive?
		return len(self.points)

	def is_leaf(self):
		return len(self.children) > 0

	def split(self):
		pass

class Point:
	"""
	Quadtree entry, represented by x and y coordinates.
	"""
	def __init__(self, x, y):
		self.region = None

		self.x = x
		self.y = y

	def move(self, to):
		if not self.region:
			raise Exception('not in tree') # TODO: better error

		pass

