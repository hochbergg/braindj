import random
import time

import player
import likeness_monitor


SECONDS = 10


######## MOCKS!! #### 

def get_likeness_value():
	# for now it's only a mock up
	return random.randint(0, 100)


def send_likeness_value(value):
	print "SENT LIKENESS VALUE: %d" % value

def send_like_score_value(value):
	print "####  SENT LIKENESS SCORE VALUE: %d" % value	





class BrainDJ(object):
	def __init__(self):
		self.player = player.MacItunesPlayer()
		self.like_score = likeness_monitor.LikenessMonitor(SECONDS)

	def start(self):
		self.player.start_song()
		while True:
			self.like_score.update(self.get_likeness_value())
			time.sleep(1)
			self.like_score.mean()

	def next_song(self):
		self.player.next_song()
		self.like_score.reset()
