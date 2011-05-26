#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

import numpy as np

from nurse.base import *
from nurse.config import Config
from nurse.sprite import *
from nurse.context import Context, ContextManager
from nurse.screen import *

from test_spatial_event import *


#-------------------------------------------------------------------------------
square_locations = np.zeros((4, 2))

def init_squares_locations(resolution):
	'''
 [[ 0, 0 ],              0 | 2
  [ 0, y ],             ---+---
  [ x, 0 ],              1 | 3
  [ x, y ]]
	'''
	x, y = (resolution[0] / 2, resolution [1] / 2)
	square_locations[1, 1] = y
	square_locations[2, 0] = x 
	square_locations[3, 0] = x
	square_locations[3, 1] = y

def move_squares_randomly(squares):
	indices = np.arange(4)
	np.random.shuffle(indices)
	for i, ind in enumerate(indices):
		squares[i].set_location(square_locations[ind])

#-------------------------------------------------------------------------------
class MoveSquaresOnCollision(ObjectProxy):
	def __init__(self, receiver, text_sprite, text_str):
		ObjectProxy.__init__(self, receiver)
		self._squares = []
		self._text_sprite = text_sprite
		self._text_str = text_str

	def add_squares(self, squares):
		self._squares += squares

	def on_collision(self, event):
		self._text_sprite.text = self._text_str
		if len(self._squares): move_squares_randomly(self._squares)


#-------------------------------------------------------------------------------
def create_colored_square(context, text, color, colorname, resolution):
	shift = (0, 0)
	size = (resolution[0] / 2, resolution[1] / 2)
	fsm = UniformLayer(colorname, context, layer=0, size=size, shift=shift,
						color=color, alpha=255)
	fsm.start()
	return MoveSquaresOnCollision(fsm, text, colorname)

def create_player(context, resolution):
	fsm = Player("player", context, layer=2, speed=180.)
	fsm.load_frames_from_filenames('__default__', ['perso.png'],
						'centered_bottom', 1)
	fsm.set_location(np.array([resolution[0] / 2, resolution[0] / 2]))
	fsm.start()
	return fsm

def create_nurse(context, text, resolution):
	x, y = (resolution[0] / 4, resolution[1] / 4)
	p1 = [x, y]
	p2 = [x, y * 3]
	p3 = [x * 3, y * 3]
	p4 = [x * 3, y]
	path = np.array([p1, p2, p3, p4])
	fsm = MovingSprite("nurse", context, layer=2, speed=120.)
	fsm.load_frames_from_filenames('__default__', ['infirmiere.png'],
							'centered_bottom', 1)
	fsm.set_path(path)
	fsm.start()
	return MoveSquaresOnCollision(fsm, text, 'nurse')

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
				(Config.resolution[1] * 15) / 16]))
	instr.stop()


	# squares
	squares = []
	for (color, colorname) in [((64, 32, 32), 'red'),
				((32, 64, 32), 'green'), 
				((32, 32, 64), 'blue'), 
				((64, 64, 32), 'yellow')]:
		s = create_colored_square(context, text, color,
					colorname, resolution)
		squares.append(s)
	for square in squares: square.add_squares(squares)
	init_squares_locations(resolution)
	move_squares_randomly(squares)

	# player and nurse
	player = create_player(context, resolution)
	nurse = create_nurse(context, text, resolution)

	# collider manager
	collider_manager = CollisionManager()
	collider_manager.add_collidable_ref_sprite(player)
	collider_manager.add_collidable_sprite(nurse) # first in the check list
	collider_manager.add_collidable_sprites(squares)

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
