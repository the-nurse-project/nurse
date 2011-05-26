#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from nurse.base import *
from nurse.config import Config
from nurse.sprite import *
from nurse.context import Context, ContextManager
from nurse.screen import *


#-------------------------------------------------------------------------------
#XXX: to be moved elsewhere : base.py ?

class ConditionalObject(Object):
	def __init__(self, name='conditional_object'):
		Object.__init__(self, name)

	def unfiltred_slot(self, slot, event):
		'''
    This function return true if the given slot/event combination is accepted
    and can be called. The parameters of this method and of the internal
    values of attributes of the current self object could be used to block
    the call of a slot.

    slot:   string name of the function to be called on self.
    event:  Event instance (pass as parameter to the slot method).

    Return True if the slot is callable.

    Note: This function must be implemented by concrete classes.
		'''
		raise RuntimeError("Unimplemented method")

	def call_slot(self, slot, event):
		'''
    This function follows the implementation if its parent's class but possibly
    filtred and block the given slot according to specific consideration
    determined by the 'unfiltred_slot' method.

    slot:   string name of the function to be called on self.
    event:  Event instance (pass as parameter to the slot method).
		'''
		if self.unfiltred_slot(slot, event):
			Object.call_slot(self, slot, event)

# XXX: la classe suivante se base sur des sprites, mais en realite seule la
# position et la bounding box de l'objet est nécessaire. Peut-être nous
# faudrait-il une classe qui comporte ses caractéristiques ?
# - est-ce qu'une classe sans image, sans frames, mais avec une position et
#   une bounding box a du sens ? Eventuellement pour définir des boundings box
#   associées à des zones invisibles / décorrélées de sprites.
class CollisionManager(Object):
	def __init__(self, name='collider_manager'):
		Object.__init__(self, name)
		self._collidable_sprites = []
		self._collidable_ref_sprite = None

	def add_collidable_ref_sprite(self, sprite):
		self._collidable_ref_sprite = sprite 

	def add_collidable_sprite(self, sprite):
		self._collidable_sprites.append(sprite)

	def add_collidable_sprites(self, sprites):
		self._collidable_sprites += sprites

	def _collide(self, bb1, bb2):
		x1, y1, w1, h1 = bb1
		x2, y2, w2, h2 = bb2
		x1_w = x1 + w1
		y1_h = y1 + h1
		x2_w = x2 + w2
		y2_h = y2 + h2
		points = [(x1, y1), (x1_w, y1), (x1_w, y1_h), (x1, y1_h)]
		in_bb = False
		for p in points:
			if (p[0] >= x2) and (p[0] <= x2_w) and\
				(p[1] >= y2) and (p[1] <= y2_h):
				in_bb = True
				break
		return in_bb

# XXX: seul le premier sprite qui collide le sprite de ref voit son slot appelé
# On pourrait ajouter un mode où tous les sprites entrant en collision voient
# leur slot respectif appelé.

# XXX: bien sûr on pourrait avoir une stratégie plus intelligente pour trouver
# le ou les sprites en collision : représentation hierarchique par exemple.
	def call_slot(self, slot, event):
		sprite_bb = self._collidable_ref_sprite.bounding_box()
		for sprite in self._collidable_sprites:
			bb = sprite.bounding_box()
			if self._collide(sprite_bb, bb):
				sprite.call_slot(slot, event)
				break


#-------------------------------------------------------------------------------
class ObjectProxy(Object):
	def __init__(self, object):
		self._object = object

	def __getattribute__(self, *args, **kwargs):
		'''
    In case of name conflicts about slots between the wrapped object and a
    class derived from ObjectProxy, the later is called first and in case of
    failure the former is called.
		'''
		try:
			return object.__getattribute__(self, *args, **kwargs)
		except AttributeError:
		        _object = object.__getattribute__(self, '_object')
			return _object.__getattribute__(*args, **kwargs)

	def call_slot(self, slot, event):
		'''
    This method allows children classes to define their own slots
		'''
		method = self.__getattribute__(slot)
		method(event)


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
