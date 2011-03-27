#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from nurse.base import *
from nurse.config import Config
from nurse.sprite import *
from nurse.context import Context, ContextManager
from nurse.screen import *

class DialogListener(Object):
	def __init__(self):
		Object.__init__(self, 'default_name')
		self.current_state = 0
	def on_dialog_start(self, event):
		print 'start'

	def on_dialog_finish(self, event):
		if self.current_state == len(self.states) - 1:
			return

		signal = (KeyBoardDevice.constants.KEYDOWN,
			KeyBoardDevice.constants.K_SPACE)
		self.states[self.current_state].add_transition(self.context, signal, 
				self.states[self.current_state + 1])
		self.current_state += 1

		#print self.next._fsm.get_location()

def create_dialog(context, msg):
	screen = Config.get_graphic_engine().get_screen()
	ws, hs = screen.get_width(), screen.get_height()
	uniform = UniformLayer('dark', context, layer=0,
				color=(0, 0, 0), alpha=128)
	uniform.start()
	
	w, h = int(ws * 0.8), int(hs * 0.3)
	x, y = (ws - w) / 2., hs - h - 50
	area = (x,y), (w,h)

	text_area = (area[0][0] + 100, area[0][1] + 30), (area[1][0] - 130, area[1][1] + 60) 
	uniform = UniformLayer('dial1', context, layer=1,
				size=(w, h), shift=(x, y),
				color=(255, 255, 255), alpha=255)
	uniform.start()
	uniform = UniformLayer('dial2', context, layer=2,
				size=(w - 2, h - 2), shift=(x + 1, y + 1),
				color=(0, 0, 64), alpha=255)
	uniform.start()
	uniform = UniformLayer('dial3', context, layer=3,
			size=(w - 4, h - 4), shift=(x + 2, y + 2),
			color=(0, 0, 128), alpha=255)
	uniform.start()
	dialog = Dialog('dialog', context, layer=4)
	
	states = []
	for i, (perso, txt, writing_machine_mode) in enumerate(msg):
		state = DialogState('state_%d' % i, txt, 'Times New Roman', 20,
				text_area, perso, 20., writing_machine_mode)
		dialog.add_state(state)
		states.append(state)

	#signal = (KeyBoardDevice.constants.KEYDOWN,
	#		KeyBoardDevice.constants.K_SPACE)
	#for i in range(len(states) - 1):
	#	states[i].add_transition(context, signal, states[i + 1])
	dialog.set_initial_state(states[0])
	dialog.set_location(text_area[0])
	dialog.start()
	next = Text('text', context, 4, '...', 'Times New Roman', 40)
	next.set_location([x+w-80,y+h-80])
	next.start()	
	sprite = StaticSprite('sprite', context, layer=4, imgname='perso.png')
	sprite.set_location(np.array([x + (180 - x) / 2, y + h / 2]))
	sprite.start() # FIXME
	dialog.dl = DialogListener()
	dialog.dl.states = states
	dialog.dl.context = context
	dialog.dl.next = next
	for state in states:
		state.connect('dialog_state_terminated', dialog.dl, 'on_dialog_finish')
		state.connect('dialog_state_started', dialog.dl, 'on_dialog_start')


#-------------------------------------------------------------------------------
def main():
	Config.backend = 'pyglet'
	Config.init()

	#FIXME : find another way to add the device
	context_manager = ContextManager()
	universe.context_manager = context_manager

	# manage context
	properties_all_active = { 'is_visible' : True, 'is_active' : True,
				'_is_receiving_events' : True} 
	context_dialog = Context("Dialog", **properties_all_active)
	context_manager.add_state(context_dialog)
	context_manager.set_initial_state(context_dialog)
	context_manager.start()

	resolution = Config.resolution
	geometry = (0, 0, resolution[0], resolution[1])

	#screen_game = VirtualScreenWorldCoordinates('main screen', geometry,
	#			player.get_location(), player)

	screen_fixed = VirtualScreenRealCoordinates('fixed screen', geometry)

	# dialog context
	msg = [
		('player', '... ...mmm...ou...ou suis-je ? ' + \
		"ahh...mes yeux ! " + \
		"Laissons leur le temps de s'habituer.", True), 
		#('player', '...%1...%1mmm...%1ou...ou suis-je ?\n' + \
		#"ahh...mes yeux !\n" + \
		#"Laissons leur le temps de s'habituer\n", True), 
		('player', "Mais%1c'est un hopital ! " + \
		"Voyons. Jambes...%1OK. Bras...%1OK. Tete...%1OK.", True),
		('nurse', "Ho! J'ai entendu du bruit dans la chambre " + \
		"d'a cote", False),
		('player', 'Bon...allons chercher des renseignements.', True)
	]
	create_dialog(context_dialog, msg)
	context_dialog.add_screen(screen_fixed)

	# FPS
	event_loop = Config.get_event_loop()
	event_loop.start()

if __name__ == "__main__" : main()
