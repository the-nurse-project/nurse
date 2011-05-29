#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from nurse.base import *
from nurse.config import Config
from nurse.sprite import *
from nurse.context import Context, ContextManager
from nurse.screen import *


def create_bg(context):
	fsm = StaticSprite('hospital', context, layer=0)
	fsm.load_from_filename('hopital.png')
	fsm.set_location(-fsm._size / 2)
	fsm.start()


def create_avatars(context):
	# path motion
	path = np.array([[0, -100], [200, -100],
		[200, 100], [-200, 100], [-200, -100]])
	path_motion = PathMotion(speed=180., start_from_location=True)
	path_motion.set_path(path)

	# nurse
	nurse = AnimatedSprite("nurse", context, layer=2)
	nurse.set_motion(path_motion)
	nurse.load_frames_from_filenames('__default__', ['infirmiere.png'],
							'centered_bottom', 1)
	nurse.start()

	# player
	player = AnimatedSprite("player", context, layer=2)
	player.set_motion(KeyboardFullArrowsMotion(speed=120.))
	player.load_frames_from_filenames('__default__', ['perso.png'],
						'centered_bottom', 1)
	player.set_location(np.array([-260, -140]))
	player.start()

	return nurse, player


class AvatarSwitcher(Object):
	def __init__(self, avatar1, avatar2):
		Object.__init__(self, 'avatar_switcher')
		self.avatars = [avatar1, avatar2]

	def on_space_press(self, event):
		motion1 = self.avatars[0].get_motion()
		motion2 = self.avatars[1].get_motion()
		self.avatars[0].set_motion(motion2, cont=True)
		self.avatars[1].set_motion(motion1, cont=True)

#-------------------------------------------------------------------------------
def main():
	# config
	Config.backend = 'pyglet'
	Config.init()

	# init
	context_manager = ContextManager()
	universe.context_manager = context_manager
	resolution = Config.resolution
	context = Context("context")
	bg = create_bg(context)

	# game context
	avatars = create_avatars(context)
	geometry = (0, 0, resolution[0], resolution[1])
	screen = VirtualScreenWorldCoordinates('screen', geometry)
	context.add_screen(screen)
	context_manager.add_state(context)
	context_manager.set_initial_state(context)
	context_manager.start()

	# avatar switch
	switcher = AvatarSwitcher(avatars[0], avatars[1])
        signal = (KeyBoardDevice.constants.KEYDOWN,
                  KeyBoardDevice.constants.K_SPACE)
        context.connect(signal, switcher, "on_space_press")

	# instruction text
	# FIXME : had a shift to center text
	shift_x = 60
	instr = Text('text', context, 4, 'hit SPACE bar', 'Times New Roman', 20)
	instr.set_location(np.array([Config.resolution[0] / 2 - shift_x,
		(Config.resolution[1] * 15) / 16]))

	# start
	event_loop = Config.get_event_loop()
	event_loop.start()

if __name__ == "__main__" : main()
