__version__ = '0.0'

class LoBotomyException(Exception):
	def __init__(self, errno):
		self.errno = errno
