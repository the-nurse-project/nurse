#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from api import *

def create_bg(context):
	fsm = StaticSprite('hospital', context, layer=0,
				imgname='hopital.png')
	fsm.set_location(np.array([-100, -100]))
	fsm.start()

def create_pause(context):
	fsm = StaticSprite('pause', context, layer=2,
				imgname='pause.png')
	fsm.set_location(np.array([0, 0]))
	fsm.start()
	uniform = UniformLayer('dark', context, layer=0,
				color=(0, 0, 0), alpha=128)
	uniform.start()


def create_player(context):
	fsm = Player("player", context, layer=2, speed=120.)
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
	fsm = MovingSprite("nurse", context, layer=2, speed=180.)
	fsm.load_frames_from_filenames('__default__', ['infirmiere.png'],
							'centered_bottom', 1)
	fsm.set_path(path)
	fsm.start()
	return fsm

def create_dialog(context):
	screen = Config.get_graphic_backend().get_screen() # FIXME
	uniform = UniformLayer('dark', context, layer=0,
				color=(0, 0, 0), alpha=128)
	uniform.start()
	w, h = screen.get_width(), screen.get_height()
	w *= 0.8
	h *= 0.3
	uniform = UniformLayer('dial1', context, layer=1, size=(w, h),
				shift=(0, h), color=(255, 255, 255), alpha=255)
	uniform.start()
	w -= 2
	h -= 2
	uniform = UniformLayer('dial2', context, layer=2, size=(w, h),
				shift=(0, h + 2), color=(0, 0, 64), alpha=255)
	uniform.start()
	w, h = screen.get_width(), screen.get_height()
	w *= 0.8 * 0.98
	h *= 0.3 * 0.9
	uniform = UniformLayer('dial3', context, layer=3, size=(w, h),
			shift=(0, h * 1.12), color=(0, 0, 128), alpha=255)
	uniform.start()
	dialog = Dialog('dialog', context, layer=4)
	msg = [
		('player', '... ...mmm...ou...ou suis-je ?' + \
		"ahh...mes yeux !" + \
		"Laissons leur le temps de s'habituer.", True), 
		#('player', '...%1...%1mmm...%1ou...ou suis-je ?\n' + \
		#"ahh...mes yeux !\n" + \
		#"Laissons leur le temps de s'habituer\n", True), 
		('player', "Mais%1c'est un hopital !\n" + \
		"Voyons. Jambes...%1OK. Bras...%1OK. Tete...%1OK.", True),
		('nurse', "Ho! J'ai entendu du bruit dans la chambre " + \
		"d'a cote", False),
		('player', 'Bon...allons chercher des renseignements.', True)
	]
	states = []
	for i, (perso, txt, writing_machine_mode) in enumerate(msg):
		state = DialogState('state_%d' % i, txt, 'Times New Roman', 20,
				400, 5, perso, 20., writing_machine_mode)
		dialog.add_state(state)
		states.append(state)

	signal = (KeyBoardDevice.constants.KEYDOWN,
			KeyBoardDevice.constants.K_SPACE)
	for i in range(len(states) - 1):
		states[i].add_transition(context, signal, states[i + 1])
	dialog.set_initial_state(states[0])
	dialog.set_location(np.array([180, 400]))
	dialog.start()
	next = Text('text', context, 4, '...', 'Times New Roman', 40)
	next.set_location(np.array([650, 480]))
	next.start()
	sprite = StaticSprite('sprite', context, layer=4, imgname='perso.png')
	sprite.set_location(np.array([-270, 180]))
	sprite.start() # FIXME

#-------------------------------------------------------------------------------
def main():
	Config.graphic_backend = Config.event_loop_backend = \
				Config.keyboard_backend = 'pyglet'
	Config.init()

	#FIXME : find another way to add the device
	context_manager = ContextManager()
	Object.universe.context_manager = context_manager

	# manage context
	properties_all_active = { 'is_visible' : True, 'is_active' : True,
				'_is_receiving_events' : True}
	properties_all_inactive = { 'is_visible' : False, 'is_active' : False,
				'_is_receiving_events' : False} 
	properties_game_inpause = { 'is_visible' : True, 'is_active' : False,
				'_is_receiving_events' : False}
	context_ingame = Context("In game")
	context_dialog = Context("Dialog", **properties_all_inactive)
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

	event = SignalEvent(None, [context_manager], signal_dialog_on)
	event.start()

	resolution = Config.resolution
	geometry = (0, 0, resolution[0], resolution[1])

	# ingame context
	create_bg(context_ingame)
	player = create_player(context_ingame)
	create_nurse(context_ingame)
	screen_game = VirtualScreen('main screen', geometry,
				player.get_location(), player)
	context_ingame.add_screen(screen_game)

	# pause context
	create_pause(context_pause)
	screen_fixed = VirtualScreen('fixed screen', geometry, (0, 0))
	context_pause.add_screen(screen_fixed)

	# dialog context
	create_dialog(context_dialog)
	context_dialog.add_screen(screen_fixed)

	# fps context
	fps_sprite = FpsSprite('fps', context_fps)
	context_fps.add_screen(screen_fixed)

	# FPS
	event_loop = Config.get_event_loop_backend()
	event_loop.start()

if __name__ == "__main__" : main()
#-------------------------------------------------------------------------------
# Notes:
# 1) gerer 2 touches actives en meme temps : Left et Up par ex (un seul event actif avec SDL)
