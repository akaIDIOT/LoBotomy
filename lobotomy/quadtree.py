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
		self.add_all(points)

	def add(self, point):
		self.root.add(point)

	def add_all(self, points):
		for point in points:
			self.add(point)

	def find_all(self, bounds):
		def collect_points(region, bounds):
			if region.overlaps(bounds):
				if region.is_leaf:
					# leaf region overlaps, return its points
					return region.points
				else:
					points = set()
					# recurse to all leaf notes, collect points from them
					for region in region.children:
						points = points.union(collect_points(region, bounds))

					# return all matched points
					return points
			else:
				# region does not overlap with bounds, return no points from it
				return set()

		# define a region representing the given bounds
		bounds = Region(bounds)
		# collect all matching points
		points = collect_points(self.root, bounds)

		# return a list representation of the final set of collected points
		return list(point for point in points if point in bounds)

	def remove(self, point):
		self.root.remove(point)

# TODO: turn into some clever extension of tuple of length 4 to allow subregion indexing
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
		(tl_x, tl_y, br_x, br_y) = bounds
		# do a sanity test on the bounds argument
		if tl_x > br_x or tl_y > br_y:
			raise ValueError('not a valid rectangle: ' + str(bounds))

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

	def overlaps(self, region):
		(a_lx, a_ty, a_rx, a_by) = self.bounds
		(b_lx, b_ty, b_rx, b_by) = region.bounds

		# no overlap if any of the conditions is false
		# see http://stackoverflow.com/questions/306316/determine-if-two-rectangles-overlap-each-other
		return a_lx < b_rx and a_rx > b_lx and a_ty < b_by and a_by > b_ty

	def split(self):
		# split required if region contains more than 4 points, split is required
		if len(self.points) > 4:
			# calculate own width and height
			(tl_x, tl_y, br_x, br_y) = self.bounds
			width = br_x - tl_x
			height = br_y - tl_y

			# create top left subregion
			tl_region = Region((tl_x, tl_y, tl_x + width / 2, tl_y + height / 2), self)
			tl_region.add_all(point for point in self.points if point in tl_region)

			# create top right subregion
			tr_region = Region((tl_x + width / 2, tl_y, br_x, tl_y + height / 2), self)
			tr_region.add_all(point for point in self.points if point in tr_region)

			# create bottom left subregion
			bl_region = Region((tl_x, tl_y + height / 2, tl_x + width / 2, br_y), self)
			bl_region.add_all(point for point in self.points if point in bl_region)

			# create bottom right subregion
			br_region = Region((tl_x + width / 2, tl_y + height / 2, br_x, br_y), self)
			br_region.add_all(point for point in self.points if point in br_region)

			# set new internal state
			self.children = (tl_region, tr_region, bl_region, br_region)
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

			# update back reference of point to region
			for point in self.points:
				point.region = self

			# remove children from self
			self.children = tuple()

			# indicate a merge was done on this region
			return True

		# indicate no merge was needed
		return False

	def __contains__(self, point):
		"""
		Returns whether the point is within the bounds of this region.

		TODO: figure out if using < for the 'upper' bound will be a problem.
		"""
		return self.bounds[0] <= point.x < self.bounds[2] and self.bounds[1] <= point.y < self.bounds[3]

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
			# remove point from instance collectino
			self.points.remove(point)
			# remove pointer to this region from removed point
			point.region = None
			# indicate that a point was removed from this leaf (parent should check for merge)
			return True
		else:
			(match, *_) = [region for region in self.children if point in region]
			if match.remove(point):
				# check for possible merge if direct child removed a point (and possibly bubble merge)
				return self.merge()
			# indicate that no point was removed from this region (parent need not check for merge)
			return False

	def remove_all(self, points):
		for point in points:
			self.remove(point)

		return self

	def __repr__(self):
		return self.__class__.__name__ + str(self.bounds)

# TODO: turn into some clever extension of namedtuple of length 2 to allow regular unpacking
class Point:
	"""
	Quadtree entry, represented by x and y coordinates and a containing region.
	"""

	def __init__(self, x, y):
		self.region = None

		self.x = x
		self.y = y

	def move(self, to):
		if not self.region:
			raise Exception('not in tree') # TODO: better error

		# save reference to old region
		old_region = self.region
		# use current region as starting point
		region = self.region
		# update state
		self.x, self.y = to

		# traverse up the tree to a region that can contain self
		while self not in region and region is not None:
			region = region.parent

		# traversed past the root
		if region is None:
			# FIXME: raising an exception at this point will break the tree, internal state was changed
			raise Exception('point not in tree bounds')

		# traverse down the tree, choosing the child region that fits every step
		while not region.is_leaf:
			(region, *_) = [region for region in region.children if self in region]

		# region is now a leaf region that can store self

		# 'move' the point from old region to new
		old_region.points.remove(self)
		region.points.add(self)
		self.region = region

		# rebalance the tree by merging old and splitting new regions
		old_region.merge()
		region.split()

	def __repr__(self):
		return self.__class__.__name__ + '({0}, {1})'.format(self.x, self.y)

