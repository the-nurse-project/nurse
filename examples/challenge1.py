#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from nurse.base import *
from nurse.config import Config
from nurse.sprite import *
from nurse.context import Context, ContextManager
from nurse.screen import *
from nurse.game.dialog import *

def create_bg(context):
	fsm = StaticSprite('hospital', context, layer=0)
	fsm.load_from_filename('hopital.png')
	fsm.set_location(np.array([-440, -300]))
	fsm.start()


def create_pause(context):
	fsm = StaticSprite('pause', context, layer=2)
	fsm.load_from_filename('pause.png')
	fsm.set_location(np.array([0, 0]))
	fsm.start()
	uniform = UniformLayer('dark', context, layer=0,
				color=(0, 0, 0), alpha=128)
	uniform.start()


def create_player(context):
	fsm = AnimatedSprite("player", context, layer=2)
	fsm.set_motion(KeyboardFullArrowsMotion(speed=120.))
	fsm.load_frames_from_filenames('__default__', ['perso.png'],
						'centered_bottom', 1)
	fsm.set_location(np.array([-260, -140]))
	fsm.start()
	return fsm


def create_nurse(context):
	p1 = [40, -200]
	p2 = [140, -200]
	p3 = [140, 50]
	p4 = [-400, 50]
	p5 = [200, 50]
	path = np.array([p1, p2, p3, p4, p5, p3, p2])
	motion = PathMotion(speed=180.)
	motion.set_path(path)
	fsm = AnimatedSprite("nurse", context, layer=2)
	fsm.set_motion(motion)
	fsm.load_frames_from_filenames('__default__', ['infirmiere.png'],
							'centered_bottom', 1)
	fsm.start()
	return fsm


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
	properties_all_inactive = { 'is_visible' : False, 'is_active' : False,
				'_is_receiving_events' : False} 
	properties_game_inpause = { 'is_visible' : True, 'is_active' : False,
				'_is_receiving_events' : False}
	context_ingame = Context("In game")

	resolution = Config.resolution
	geometry = (0, 0, resolution[0], resolution[1])
	screen_fixed = VirtualScreenRealCoordinates('fixed screen', geometry)
	msg = [ ('player', '... ...mmm...ou...ou suis-je ? ' + \
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

	context_pause = Context("Pause", **properties_all_inactive)
	context_fps = Context("fps", **properties_all_inactive)
	signal_pause = (KeyBoardDevice.constants.KEYDOWN,
				KeyBoardDevice.constants.K_p)
	signal_dialog_on = "dialog_on"
	signal_dialog_off = "dialog_off"
	context_ingame.add_transition(context_manager, signal_pause,
		context_pause, properties_game_inpause, properties_all_active)
	context_pause.add_transition(context_manager, signal_pause,
		context_ingame, properties_all_inactive, properties_all_active)
	context_ingame.add_transition(context_manager, signal_dialog_on,
		context_dialog, properties_game_inpause, properties_all_active)
	context_dialog.add_transition(context_manager, signal_dialog_off,
		context_ingame, properties_all_inactive, properties_all_active)
	context_manager.add_state(context_ingame)
	context_manager.add_state(context_pause)
	context_manager.add_state(context_dialog)
	context_manager.add_state(context_fps)
	context_manager.set_initial_state(context_ingame)
	context_manager.start()

	event = SignalEvent(None, context_ingame, 'on_transition',
					signal_dialog_on)
	event.start()


	# ingame context
	create_bg(context_ingame)
	player = create_player(context_ingame)
	create_nurse(context_ingame)
	screen_game = VirtualScreenWorldCoordinates('main screen', geometry,
				player.get_location(), player)
	context_ingame.add_screen(screen_game)

	# pause context
	create_pause(context_pause)
	context_pause.add_screen(screen_fixed)

	context_dialog.add_screen(screen_fixed)

	# fps context
	fps_sprite = FpsSprite('fps', context_fps)
	context_fps.add_screen(screen_fixed)

	# FPS
	event_loop = Config.get_event_loop()
	event_loop.start()

if __name__ == "__main__" : main()
