#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from nurse.base import *
from nurse.config import Config
from nurse.sprite import *
from nurse.context import Context, ContextManager
from nurse.screen import *

#-------------------------------------------------------------------------------
class ChangeTextOnCollision(ObjectProxy):
	def __init__(self, sprite_receiver, text_sprite, text_str):
		ObjectProxy.__init__(self, sprite_receiver)
		self._text_sprite = text_sprite
		self._text_str = text_str

	def on_collision(self, event):
		self._text_sprite.text = self._text_str


#-------------------------------------------------------------------------------
def create_bg_left(context, text, resolution):
	shift = (0, 0)
	size = (resolution[0] / 2, resolution[1])
	fsm = UniformLayer('left', context, layer=0, size=size, shift=shift,
				color=(64, 32, 32), alpha=255)
	fsm.start()
	return ChangeTextOnCollision(fsm, text, 'left')

def create_bg_right(context, text, resolution):
	shift = (resolution[0] / 2, 0)
	size = (resolution[0] / 2, resolution[1])
	fsm = UniformLayer('right', context, layer=0, size=size, shift=shift,
				color=(32, 64, 32), alpha=255)
	fsm.start()
	return ChangeTextOnCollision(fsm, text, 'right')

def create_player(context, resolution):
	fsm = Player("player", context, layer=2, speed=120.)
	fsm.load_frames_from_filenames('__default__', ['perso.png'],
						'centered_bottom', 1)
	fsm.set_location(np.array([resolution[0] / 2, resolution[0] / 2]))
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
	context = Context("context")

	# status text
	# FIXME : had a shift to center text
	shift_x = 90
	text = Text('text', context, 4, '????', 'Times New Roman', 80)
	text.set_location(np.array([Config.resolution[0] / 2 - shift_x, 
				Config.resolution[1] / 32]))
	text.stop()

	# instruction text
	# FIXME : had a shift to center text
	shift_x = 60
	instr = Text('text', context, 4, 'hit SPACE bar', 'Times New Roman', 20)
	instr.set_location(np.array([Config.resolution[0] / 2 - shift_x, 
				(Config.resolution[1] * 7) / 8]))
	instr.stop()



	# background
	bg_left = create_bg_left(context, text, resolution)
	bg_right = create_bg_right(context, text, resolution)
	player = create_player(context, resolution)

	# collider manager
	collider_manager = CollisionManager()
	collider_manager.add_collidable_ref_sprite(player)
	collider_manager.add_collidable_sprites([bg_left, bg_right])

	signal = (KeyBoardDevice.constants.KEYDOWN,
			KeyBoardDevice.constants.K_SPACE)
	context.connect(signal, collider_manager,
			"on_collision", asynchronous=False)

	# context
	geometry = (0, 0, resolution[0], resolution[1])
	screen = VirtualScreenRealCoordinates('screen', geometry)
	context.add_screen(screen)
	context_manager.add_state(context)
	context_manager.set_initial_state(context)
	context_manager.start()

	# start
	event_loop = Config.get_event_loop()
	event_loop.start()

if __name__ == "__main__" : main()
