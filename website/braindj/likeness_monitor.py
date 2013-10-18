from collections import deque

SECONDS = 10

class SizedDeque(deque):
	def __init__(self, size=SECONDS):
		self.size = size
		deque.__init__(self)
	def append(self, attr):
		if len(self) == self.size:
			self.popleft()
		deque.append(self, attr)

class LikenessMonitor(object):
	def __init__(self, seconds=SECONDS):
		self.seconds = seconds
		self.likes = SizedDeque(seconds)

	def update(self, num):
		self.likes.append(num)

	def mean(self):
		return float(sum(self.likes)) / len(self.likes)

	def reset(self):
		self.likes = SizedDeque(self.seconds)

	def __repr__(self):
		return "Likes<%s>" % repr(self.likes)
