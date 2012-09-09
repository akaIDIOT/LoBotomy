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

	def __init__(self, dimensions, *points):
		"""
		Creates a new QuadTree spanning the given dimensions, containing the
		specified points.
		"""
		self.root = Region(dimensions)

		for point in points:
			self.add(point)

	def add(self, point):
		self.root.add(point)

	def add_all(self, points):
		for point in points:
			self.add(point)

# TODO: tuen into some clever extension of tuple of length 4 to allow subregion indexing
class Region:
	"""
	Index region withing a QuadTree, containing either child regions or leaves
	(points). Contains a reference back to its parent, so the tree of regions
	can be traversed in both directions.
	"""

	def __init__(self, bounds, parent = None, *points):
		"""
		Creates a new Region spanning the given dimensions.
		"""
		self.bounds = bounds
		self.parent = parent
		self.children = []
		self.points = set()
		self.add_all(points)

	def __len__(self):
		if self.is_leaf:
			return len(self.points)
		else:
			return sum(map(len, self.children))

	@property
	def is_leaf(self):
		return len(self.children) is 0

	def split(self):
		# split required if region contains more than 4 points, split is required
		if len(self.points) > 4:
			# calculate own width and height
			((tl_x, tl_y), (br_x, br_y)) = self.bounds
			width = br_x - tl_x
			height = br_y - tl_y

			# FIXME: __in__ matching could put points in multiple regions

			# create top left subregion
			tl_region = Region((
				(tl_x, tl_y),
				(tl_x + width / 2, tl_y + height / 2)
			), self)
			tl_region.add_all(point for point in self.points if point in rl_region)

			# create top right subregion
			tr_region = Region((
				(tl_x + width / 2, tl_y),
				(br_x, tl_y + height / 2)
			), self)
			tr_region.add_all(point for point in self.points if point in tr_region)

			# create bottom left subregion
			bl_region = Region((
				(tl_x, tl_y + height / 2),
				(tl_x + width / 2, br_y)
			), self)
			rl_region.add_all(point for point in self.points if point in rl_region)

			# create bottom right subregion
			br_region = Region((
				(tl_x + width / 2, tl_y + height / 2),
				(br_x, br_y)
			), self)
			br_region.add_all(point for point in self.point if point in br_region)

			# set new internal state
			self.children = [tl_region, tr_region, bl_region, br_region]
			self.points = set()

	def merge(self):
		# merge required if not a leaf but contains 4 or less points
		if not self.is_leaf and len(self) <= 4:
			for region in self.children:
				# tell the subregions to merge ('issue' could be recursive with 3 out of 4 subregions being empty)
				region.merge()
				# move all points from subregion to self
				self.points = self.points.union(region.points)
				# remove state from subregion
				region.parent = None
				region.points = set()

			# remove children from self
			self.children = []

	def __in__(self, point):
		"""
		Returns whether the point is within the bounds of this region.

		TODO: figure out if using < for the 'upper' bound will be a problem.
		"""
		return point.x >= self.bounds[0][0] and point.x < self.bounds[1][0] and point.y >= self.bounds[0][1] and point.y < self.bounds[1][1]

	def add(self, point):
		if point not in self:
			raise Exception('point not in region') # TODO: better error

		if self.is_leaf:
			point.region = self
			self.points.add(point)
			# split self if required
			self.split()
		else:
			# get the first match (should be the only one), save the rest in _
			# (using only 1 match is important, as it might be included twice in the tree otherwise)
			(match, *_) = [region for region in self.children if point in region]
			match.add(point)

		# return 'left operand' of addition: self
		return self

	def add_all(self, points):
		for point in points:
			self.add(point)

		return self

	def remove(self, point):
		if point not in self:
			raise Exception('point not in region') # TODO: better error

		if self.is_leaf:
			self.points.remove(point)
			# merge self if required
			self.merge()
		else:
			(match, *_) = [region for region in self.children if point in region]
			match.remove(point)

		return self

	def remove_all(self, points):
		for point in points:
			self.remove(point)

		return self

# TODO: turn into some clever extension of namedtuple of length 2 to allow regular unpacking
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

