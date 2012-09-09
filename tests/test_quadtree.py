import unittest

from lobotomy.quadtree import Point, QuadTree, Region

class TestRegion(unittest.TestCase):
	def setUp(self):
		# setup a simple region
		self.region = Region((0, 0, 1, 1))
		self.four_points = [Point(.1, .1), Point(.2, .2), Point(.3, .3), Point(.4, .4)]
		self.more_points = [Point(.1, .2), Point(.2, .3), Point(.3, .4), Point(.4, .5)]

	def test_init(self):
		# test constructor in regular manner
		Region((0, 0, 1, 1))
		# test inverted rectangle
		self.assertRaises(ValueError, Region, (1, 1, 0, 0))

	def test_insertion(self):
		# insert 4 points (should just work)
		self.region.add_all(self.four_points)
		self.assertEqual(len(self.region), 4)
		self.assertTrue(self.region.is_leaf)
		# remove the points and assert manually
		self.region.points = set()
		for point in self.four_points:
			self.region.add(point)
		self.assertEqual(len(self.region), 4)
		self.assertTrue(self.region.is_leaf)
		# inserting a bunch more nodes should cause a split in the top left corner
		self.region.add_all(self.more_points)
		self.assertEqual(len(self.region), 8)
		self.assertFalse(self.region.is_leaf)
		# top left region should contain 7 / 8 of the nodes (< split point at (.5, .5))
		self.assertEqual(len(self.region.children[0]), 7)
		# top left child of top left region should contain 3 / 7 of the nodes (< split point at (2.5, 2.5))
		self.assertEqual(len(self.region.children[0].children[0]), 3)

	def test_removal(self):
		# insert 4 points (should just work)
		self.region.add_all(self.four_points)
		self.assertEqual(len(self.region), 4)
		self.assertTrue(self.region.is_leaf)
		# remove a single node
		self.region.remove(self.four_points[0])
		self.assertEqual(len(self.region), 3)
		self.assertTrue(self.region.is_leaf)
		# remove the other nodes
		self.region.remove_all(self.four_points[1:])
		self.assertEqual(len(self.region), 0)
		self.assertTrue(self.region.is_leaf)
		# cause two splits
		self.region.add_all(self.four_points)
		self.region.add_all(self.more_points)
		self.assertEqual(len(self.region), 8)
		self.assertFalse(self.region.is_leaf)
		# cause a merge
		self.region.remove_all(self.more_points)
		self.assertEqual(len(self.region), 4)
		self.assertTrue(self.region.is_leaf)

	def test_is_leaf(self):
		# fresh empty region should be a leaf
		self.assertTrue(self.region.is_leaf)
		# region with a single Point in it should be a leaf
		self.region.add(Point(.5, .5))
		self.assertTrue(self.region.is_leaf)
		# region with five points in it should not be a leaf
		self.region.add_all(self.four_points)
		self.assertFalse(self.region.is_leaf)

	def test_containment(self):
		# point half way should be in region
		self.assertTrue(Point(.5, .5) in self.region)
		# point on left and top boundaries should be in region
		self.assertTrue(Point(0, .5) in self.region)
		self.assertTrue(Point(.5, 0) in self.region)
		self.assertTrue(Point(0, 0) in self.region)
		# point outside the boundaries should not be in region
		self.assertFalse(Point(0, 2) in self.region)
		self.assertFalse(Point(2, 0) in self.region)
		self.assertFalse(Point(-1, -1) in self.region)
		self.assertFalse(Point(2, 2) in self.region)
		# point on right and bottom boundaries should not be in region
		self.assertFalse(Point(0, 1) in self.region)
		self.assertFalse(Point(1, 0) in self.region)
		self.assertFalse(Point(1, 1) in self.region)

	def test_length(self):
		# empty region should have length 0
		self.assertEqual(len(self.region), 0)
		# adding a single point should make the length 1
		self.region.add(Point(.5, .5))
		self.assertEqual(len(self.region), 1)
		# causing splits should calculate length recursively
		self.region.add_all(self.four_points)
		self.assertEqual(len(self.region), 5)
		# removing the points should cause the length to revert back to 1
		self.region.remove_all(self.four_points)
		self.assertEqual(len(self.region), 1)

	# TODO: test overlaps

class TestQuadTree(unittest.TestCase):
	# TODO: test constructor
	# TODO: test find_all
	pass

class TestMove(unittest.TestCase):
	# TODO: test moving point to the same region
	# TODO: test moving point to close region
	# TODO: test moving point to region requiring traversing through root
	# TODO: test moving point outside of tree
	pass

