import numpy as np

from base import Object
from state_machine import StateMachine, State
from config import Config
from backends import KeyBoardDevice
from motion import *


''' This module groups standard sprites.
.. module:: sprites
.. moduleauthor:: Matthieu Perrot <matthieu.perrot@gmail.com>
'''


#-------------------------------------------------------------------------------
class Sprite(StateMachine):
	def __init__(self, name='sprite', context=None, layer=1):
		'''
    name:  name of the sprite
    layer: (default: 1 since 0 is reserved for background)
		'''
		StateMachine.__init__(self, name, context)
		if context is None: context = Config.get_default_context()
		context.add_visible_data(self, layer)
		self._layer = layer
		self._location = np.zeros(2)
		self._size = np.zeros(2)
		self._bb_center = np.zeros(2)
		self.set_motion(no_motion)

	def set_motion(self, motion, cont=False):
		'''
    Replace the current motion by the given one.

    Parameters:
  
    motion : Motion instance
        The motion to be attached to this sprite.
    cont : bool
        If false the motion is reinitialized.
	If true the motion is continued.
		'''
		if motion.get_context() is None:
			motion.set_context(self.get_context())
		self._motion = motion
		motion.start()
		if cont:
			motion.cont(self)
		else:	motion.init(self)

	def get_motion(self):
		'''
    Return the current motion.
		'''
		return self._motion

	def update(self, dt):
		'''
    Update sprite location (in world coordinates) according to its
    control state and current active frame
		'''
		self._motion.update_sprite(self, dt)

	def bounding_box(self):
		return (self._location[0] - self._bb_center[0], 
			self._location[1] - self._bb_center[1], 
			self._size[0], self._size[1])

	def get_location(self):
		'''
    Return sprite location in world coordinate system
		'''
		return self._location

	def set_location(self, location):
		'''
    set sprite location in world coordinate system
		'''
		self._location = location
		self.emit("location_changed", location)


class AnimatedSprite(Sprite):
	def __init__(self, name='animated_sprite', context=None, layer=1):
		'''
    name:  name of the sprite
    layer: (default: 1 since 0 is reserved for background)
		'''
		Sprite.__init__(self, name, context, layer)
		self._current_frame_id = 0
		self._frames = {}
		self._frames_center_location = {}
		self._refresh_delay = {}

	def load_frames_from_filenames(self, state,
		frames_fnames=[], center_location=(0,0), fps=30):
		'''
    Load frames from images (one image per file) for a given state

    state:           A valid state of the Sprite State Machine.
                     If state equals __default__, these frames are used for
		     each state without any frames.
		     If frames_fnames is [] then no sprite is displayed for
		     the given state.
    frames_fnames:   liste of filenames.
    center_location: - tuple of coordinates in pixel from the bottom left corner
                       of the images (the same shift for all images).
		     - list of coordinates in pixel from the bottom left corner
		       of the images (one shift per image).
		  or - 'centered': the center is centered on the images.
		  or - 'centered_bottom': the center is centered on the bottom
		       of the images.
    fps:             number of frames per seconds.
		'''
		self._frames[state] = [ \
			Config.get_graphic_engine().load_image(fname) \
			for fname in frames_fnames]
		self._refresh_delay[state] = int(1000 / fps)
		loc = []
		for img in self._frames[state]:
			width, height = img.get_size()
			if width > self._size[0]: self._size[0] = width
			if height > self._size[1]: self._size[1] = height
		if isinstance(center_location, str):
			for img in self._frames[state]:
				width, height = img.get_size()
				if center_location == 'centered':
					loc.append(np.array([width, height])/2.)
				elif center_location == 'centered_bottom':
					loc.append(np.array([width/2., height]))
		elif isinstance(center_location, list):
			loc = center_location
		else:	loc = [center_location] * len(self._frames[state])
		if center_location == 'centered':
			self._bb_center = self._size / 2.
		elif center_location == 'centered_bottom':
			self._bb_center = self._size
			self._bb_center[0] /= 2.
		self._frames_center_location[state] = loc

	def get_frame_infos(self, time):
		'''
    Return frame infos for a given time : image uuid, center location
		'''
		state = self._current_state
		try:
			frames = self._frames[state]
		except KeyError:
			state = '__default__'
			frames = self._frames[state]
			if len(frames) == 0: return None, None
		refresh_delay = self._refresh_delay[state]
		frames_center_location = self._frames_center_location[state]
		frames_n = len(frames)
		id = int((time % (refresh_delay * frames_n)) / refresh_delay)
		return frames[id], frames_center_location[id]


class StaticSprite(Sprite):
	def __init__(self, name, context, layer=0):
		Sprite.__init__(self, name, context, layer)

	def load_from_filename(self, imgname, center_location=(0,0)):
		gfx = Config.get_graphic_engine()
		self._img_proxy = gfx.load_image(imgname)
		width, height = self._img_proxy.get_size()
		if width > self._size[0]:
			self._size[0] = width
		if height > self._size[1]:
			self._size[1] = height
		if isinstance(center_location, str):
			if center_location == 'centered':
				self._bb_center = self._size / 2.
			elif center_location == 'centered_bottom':
				self._bb_center = self._size.copy()
				self._bb_center[0] /= 2.
		else:
			self._bb_center = np.asarray(center_location)

	def get_frame_infos(self, time=0):
		return self._img_proxy, self._bb_center


class UniformLayer(Sprite):
	def __init__(self, name, context, layer=2, size=None,
			shift=(0, 0), center_location=(0,0),
			color=(0, 0, 0), alpha=128):
		Sprite.__init__(self, name, context, layer)
		gfx = Config.get_graphic_engine()
		self._img_proxy= gfx.get_uniform_surface(shift, size,
							color, alpha)
		if isinstance(center_location, str):
			width, height = np.array(self._img_proxy.get_size())
			if center_location == 'centered':
				self._bb_center = np.array([width, height]) / 2.
			elif center_location == 'centered_bottom':
				self._bb_center = np.array([width / 2., height])
			elif center_location == 'top_left':
				self._bb_center = np.array([0., 0.])
		else:
			self._bb_center = np.asarray(center_location)
		self._size = size
		self.set_location(shift)

	def get_frame_infos(self, time):
		return self._img_proxy, self._bb_center



class Dialog(Sprite):
	def __init__(self, name='dialog', context=None, layer=2):
		Sprite.__init__(self, name, context, layer)

	def update(self, dt):
		Sprite.update(self, dt) # for motions
		self._current_state.update(dt)


class Text(Sprite):
	def __init__(self, name='text', context=None, layer=2,
		text='...', font='Times New Roman', font_size=20):
		Sprite.__init__(self, name, context, layer)
		self.text = text
		self.font = font
		self.font_size = font_size
		self.backend_repr = None

	def update(self, dt): #FIXME : on devrait pas avoir a updater le dialog?
		Sprite.update(self, dt) # for motions
		self.backend_repr = Config.get_graphic_engine().load_text(\
				self.text, self.font, self.font_size,
				self._location[0], self._location[1])


class FpsSprite(Sprite):
	'''Compute and display current FPS (Frames per second) rate.'''
	def __init__(self, name='fps', context=None, layer=3,
		fg_color=(255, 255, 255), bg_color=(0, 0, 0)):
		Sprite.__init__(self, name, context, layer)
		if context is None: context = Config.get_default_context()
		self.fg_color = fg_color
		self.bg_color = bg_color

	def update(self, dt):
		pass


#-------------------------------------------------------------------------------
# XXX: la classe suivante se base sur des sprites, mais en realite seule la
# position et la bounding box de l'objet est necessaire. Peut-etre nous
# faudrait-il une classe qui comporte ses caracteristiques ?
# - est-ce qu'une classe sans image, sans frames, mais avec une position et
#   une bounding box a du sens ? Eventuellement pour definir des boundings box
#   associees a des zones invisibles / decorrelees de sprites.
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

# XXX: seul le premier sprite qui collide le sprite de ref voit son slot appele
# On pourrait ajouter un mode ou tous les sprites entrant en collision voient
# leur slot respectif appele.

# XXX: bien sur on pourrait avoir une strategie plus intelligente pour trouver
# le ou les sprites en collision : representation hierarchique par exemple.
	def call_slot(self, slot, event):
		sprite_bb = self._collidable_ref_sprite.bounding_box()
		for sprite in self._collidable_sprites:
			bb = sprite.bounding_box()
			if self._collide(sprite_bb, bb):
				sprite.call_slot(slot, event)
				break
