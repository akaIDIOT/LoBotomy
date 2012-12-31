# make sure flake8 ignores this file: flake8: noqa

# XXX: PRELIMINARY DEFINITIONS, SUBJECT TO CHANGE WITHOUT NOTICE

import math

def move_cost(distance):
    '''
    Returns the cost (in energy) of moving the given distance
    '''
	return distance * 2.0

def move_cost_inverse(cost):
    '''
    Returns the distance one could move with the given energy cost
    '''
    return cost / 2.0

def scan_cost(radius):
    '''
    Returns the cost (in energy) of scanning the given radius
    '''
	return (radius * 2.0) ** 2.0

def scan_cost_inverse(cost):
    '''
    Returns the radius one could scan with the given energy cost
    '''
    return math.sqrt(cost) / 2.0

def fire_cost(distance, radius, charge):
    '''
    Returns the cost (in energy) of firing the given distance, with the given
    radius and charge
    '''
    return distance + math.pi * radius ** 2.0 * charge
