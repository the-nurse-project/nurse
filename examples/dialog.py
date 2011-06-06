#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from nurse.base import *
from nurse.config import Config
from nurse.sprite import *
from nurse.context import Context, ContextManager
from nurse.screen import *
from nurse.game.dialog import *


#-------------------------------------------------------------------------------
def main():
	Config.backend = 'pyglet'
	Config.init()

	#FIXME : find another way to add the device
	context_manager = ContextManager()
	universe.context_manager = context_manager

	resolution = Config.resolution
	geometry = (0, 0, resolution[0], resolution[1])
	screen_fixed = VirtualScreenRealCoordinates('fixed screen', geometry)

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

	context_dialog = DialogContext("Dialog", msg)
	context_dialog.add_screen(screen_fixed)
	context_manager.add_state(context_dialog)
	context_manager.set_initial_state(context_dialog)
	context_manager.start()

	# FPS
	event_loop = Config.get_event_loop()
	event_loop.start()

if __name__ == "__main__" : main()
