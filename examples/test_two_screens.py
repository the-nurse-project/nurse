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
	fsm.set_location(np.array([-440, -300]))
	fsm.start()


def create_pause(context):
	screen = Config.get_graphic_engine().get_screen()
	w, h = screen.get_width(), screen.get_height()
	fsm = StaticSprite('pause', context, layer=2)
	fsm.load_from_filename('pause.png')
	# FIXME : coordinates should be in screen coordinates
	size = fsm._size
	fsm.set_location(np.array([(w - size[0]) / 2, (h - size[1]) / 2]))
	fsm.start()


def create_perso_left(context):
	p1 = [0, -100]
	p2 = [200, -100]
	p3 = [200, 100]
	p4 = [-200, 100]
	p5 = [-200, -100]
	path = np.array([p1, p2, p3, p4, p5])
	motion = PathMotion(speed=180.)
	motion.set_path(path)
	fsm = AnimatedSprite("nurse", context, layer=2)
	fsm.set_motion(motion)
	fsm.load_frames_from_filenames('__default__', ['infirmiere.png'],
							'centered_bottom', 1)
	fsm.start()
	return fsm


def create_perso_right(context):
	p1 = [0, -100]
	p2 = [-200, -100]
	p3 = [-200, 100]
	p4 = [200, 100]
	p5 = [200, -100]
	path = np.array([p1, p2, p3, p4, p5])
	motion = PathMotion(speed=180.)
	motion.set_path(path)
	fsm = AnimatedSprite("perso", context, layer=2)
	fsm.set_motion(motion)
	fsm.load_frames_from_filenames('__default__', ['perso.png'],
							'centered_bottom', 1)
	fsm.start()
	return fsm


#-------------------------------------------------------------------------------
def main():
	# config
	Config.backend = 'pyglet'
	Config.init()

	# init
	context_manager = ContextManager()
	universe.context_manager = context_manager
	resolution = Config.resolution
	context_split = Context("context split")
	create_bg(context_split)

	# left context
	perso_left = create_perso_left(context_split)
	geometry_left = (0, 0, resolution[0] / 2, resolution[1])
	screen_left = VirtualScreenWorldCoordinates('screen left',
			geometry_left, perso_left.get_location(), perso_left)
	context_split.add_screen(screen_left)
	context_manager.add_state(context_split)

	# right context
	perso_right = create_perso_right(context_split)
	geometry_right = (resolution[0] / 2, 0, resolution[0] / 2,resolution[1])
	screen_right = VirtualScreenWorldCoordinates('screen right',
			geometry_right, perso_right.get_location(), perso_right)
	context_split.add_screen(screen_right)
	context_manager.add_state(context_split)

	context_manager.set_initial_state(context_split)
	context_manager.start()

	# context pause
	context_pause = Context("context pause")
	create_pause(context_pause)
	context_manager.add_state(context_pause)
	geometry = (0, 0, resolution[0], resolution[1])
	screen = VirtualScreenRealCoordinates('screen', geometry)
	context_pause.add_screen(screen)

	# start
	event_loop = Config.get_event_loop()
	event_loop.start()

if __name__ == "__main__" : main()
