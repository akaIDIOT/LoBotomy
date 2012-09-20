# make sure flake8 ignores this file: flake8: noqa

# XXX: PRELIMINARY DEFINITIONS, SUBJECT TO CHANGE WITHOUT NOTICE

import math

def move_cost(distance):
	return distance * 2

def scan_cost(radius):
	return (radius * 2) ** 2

def fire_cost(distance, radius, charge):
	return distance + math.pi * radius ** 2 * charge

