#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from nurse import *
from nurse.base import *
from nurse.config import *
from nurse.sprite import *
from nurse.context import *
from nurse.backends import *
from nurse.screen import *


class Incrementator(Object):
	def __init__(self):
		Object.__init__(self, 'default_name')
	def on_space_press(self, event):
		if self.text.text == 'plop':
			self.text.text = 'plip'
		else:
			self.text.text = 'plop'
	def on_time_event(self, event):
		if self.text.text == 'plup':
			self.text.text = 'plap'
		else:
			self.text.text = 'plup'

class Timer(Object):
	def start(self):
		import pyglet
		pyglet.clock.schedule_interval ( self.tick, 1 )
	def tick(self,dt):
		self.emit("time_event")
		print 'hello', dt
		
#-------------------------------------------------------------------------------
def main():
	Config.backend = 'pyglet'
	#Config.graphic_backend = Config.event_loop_backend = \
	#				Config.keyboard_backend = 'pyglet'
	Config.init()

	context_manager = ContextManager()
	universe.context_manager = context_manager

	properties_all_active = { 'is_visible' : True, 'is_active' : True,
				'_is_receiving_events' : True}
	properties_all_inactive = { 'is_visible' : False, 'is_active' : False,
				'_is_receiving_events' : False}
	context = Context("Pause", **properties_all_active)

	context_manager.add_state(context)
	context_manager.set_initial_state(context)
	context_manager.start()

	text = Text('text', context, 4, 'plop', 'Times New Roman', 40)
	text.set_location(np.array([650, 480]))
	text.start()
	screen = VirtualScreen('main screen')
	context.add_screen(screen)
	incrementator = Incrementator()
	incrementator.text = text
	context.connect((KeyBoardDevice.constants.KEYDOWN, KeyBoardDevice.constants.K_SPACE),
			incrementator, "on_space_press" )

	t =  Timer('test')
	t.connect("time_event", incrementator, "on_time_event" )
	t.start()
	event_loop = Config.get_event_loop()
	event_loop.start()

if __name__ == "__main__" : main()
#-------------------------------------------------------------------------------
# Notes:
# 1) gerer 2 touches actives en meme temps : Left et Up par ex (un seul event actif avec SDL)
