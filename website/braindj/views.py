import json
from collections import deque
import random

from django.http import HttpResponse
import likeness_monitor
import player


SECONDS = 1


class JsonResponse(HttpResponse):

	def __init__(self, data, status=200):
		content = json.dumps(data, separators=(',', ':'))
		super(JsonResponse, self).__init__(
			content, content_type='application/json', status=status)


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
		if len(self.likes) == 0:
			return 0
		return sum(map(float,self.likes)) / len(self.likes)

	def reset(self):
		self.likes = SizedDeque(self.seconds)

	def __repr__(self):
		return "Likes<%s>" % repr(self.likes)


class BrainDJ(object):
	def __init__(self):
		self.player = player.MacItunesPlayer()
		self.like_score = LikenessMonitor(SECONDS)
		self.active_moods = [True, True, False]
		self.thresholds = (0, 4, 8, 10)

	def start(self):
		self.player.start_song()

	def set_user_state(self, value):
		self.like_score.update(value)

	def next_song(self):
		self.player.next_song()
		self.like_score.reset()

	def current_likeness(self):
		if len(self.like_score.likes) == 0:
			return 0
		return self.like_score.likes[-1]

	def change_mood(self, mood):
		self.active_moods[int(mood)] = not self.active_moods[int(mood)]

	def should_change_song(self):
		state = self.like_score.mean()

		if not self.active_moods[0]:
			if self.thresholds[0] <= state < self.thresholds[1]:
				return True
		if not self.active_moods[1]:
			if self.thresholds[1] <= state < self.thresholds[2]:
				return True
		if not self.active_moods[2]:
			if self.thresholds[2] <= state < self.thresholds[3]:
				return True
		return False

dj = BrainDJ()
moods = [False, False, False]

def start(request):
	dj.start()
	return JsonResponse({})

def current_likeness(request):
	if dj.should_change_song():
		dj.next_song()
	return JsonResponse({'current_likeness': dj.current_likeness()})

def state(request):
	pass

def set_state(request):
	mode = request.GET.get('index')
	dj.change_mood(mode)
	return JsonResponse({})

def set_user_state(request):
	value = request.GET.get('value')
	dj.set_user_state(value)
	print 'user state', value
	return JsonResponse({})

def play(request):
	player.start_song()

def next(request):
	player.next_song()

def pause(request):
	player.pause()

def get_current_song(request):
	return JsonResponse({'current_song': dj.player.get_current_song()})
