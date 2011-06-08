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

	def get_frame_infos(self, time):
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



class DialogState(State):
	def __init__(self, name='text', text='...', font='Times New Roman',
		font_size=20, max_width=100, max_lines=3, perso=None,
		char_per_sec=5., writing_machine_mode=True):
		State.__init__(self, name)
		self._text = text
		self.font = font
		self.font_size = font_size
		self.max_width = max_width
		self.max_lines = max_lines
		self.perso = perso
		if writing_machine_mode:
			self.char_delay = 1000. / char_per_sec
		else:	self.char_delay = 0
		self.writing_machine_mode = writing_machine_mode
		self.list_backend_repr = []
		self._current_time = 0
		self._current_indice = 0
		self._current_text = ''
		self._current_height = 0
	
	def _update_chars(self, n):
		max_ind = len(self._text)
		ind = self._current_indice
		if ind == max_ind: return
		new_ind = ind + n
		if new_ind > max_ind: new_ind = max_ind
		new_text = self._text[ind:new_ind]
		self._current_text += new_text
		self._current_indice = new_ind
		anchor_x, anchor_y = self._fsm.get_location()
		repr = Config.get_graphic_engine().load_text(\
				self._current_text, self.font, self.font_size,
				anchor_x, anchor_y + self._current_height)
		if repr.content_width <= self.max_width:
			if len(self.list_backend_repr) == 0:
				self.list_backend_repr.append(repr)
			else:	self.list_backend_repr[-1] = repr
		else:
			self._current_height += repr.content_height
			repr = Config.get_graphic_engine().load_text(\
				new_text, self.font, self.font_size,
				anchor_x, anchor_y + self._current_height)
			self.list_backend_repr.append(repr)
			self._current_text = new_text
			if len(self.list_backend_repr) > self.max_lines:
				del self.list_backend_repr[0]
				Config.get_graphic_engine().shift_text(self,
							repr.content_height)
				self._current_height -= repr.content_height
				
	def update(self, dt):
		self._current_time += dt	
		if self._current_time >= self.char_delay:
			if self.char_delay == 0:
				n = len(self._text)
			else:	n = int(self._current_time / self.char_delay)
			self._update_chars(n)
			self._current_time -= n * self.char_delay
		


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
