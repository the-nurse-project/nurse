import numpy as np

from base import Object
from state_machine import StateMachine, State
from config import Config
from backends import KeyBoardDevice


#-------------------------------------------------------------------------------
class Motion(StateMachine):
	def __init__(self, name='motion', context=None, speed=100.):
		'''
    speed: speed in world-coordinate metric per seconds

		'''
		StateMachine.__init__(self, name, context)
		self._speed = speed
		self._layer = layer

	def update(self, dt):
		pass

	def update_sprite(self, sprite, dt):
		raise NotImplementedError

	def init(self, sprite):
		pass

	def cont(self, sprite):
		pass

class StaticMotion(Motion):
	def __init__(self, name='static_motion', context=None):
		Motion.__init__(self, name, context)

	def update_sprite(self, sprite, dt):
		pass

static_motion = StaticMotion()


class PathMotion(Motion):
	Start_to_End = 0
	End_to_Start = 1
	def __init__(self, name='path_motion', context=None, speed=100.,
					start_from_location=False):
		'''
    path : list of world coordinates

		'''
		Motion.__init__(self, name, context, speed)
		self._path = None
		self._way = PathMotion.Start_to_End
		self._indice_states = [\
			State("rest"), State("left"), State("left-up"),
			State("up"), State("right-up"),
			State("right"), State("right-down"),
			State("down"), State("left-down")]
		self._state_name_to_id = {"rest" : 0, "left" : 1, "left-up" : 2,
				'up' : 3, 'right-up' : 4, 'right' : 5,
				'right-down' : 6, 'down' : 7, 'left-down' : 8}
		for state in self._indice_states: self.add_state(state)
		self._directions = np.array([\
			[-1., -1., 0, 1., 1., 1., 0, -1.],
			[0, -1., -1., -1., 0, 1., 1., 1.]])
		self._directions /= np.sqrt((self._directions ** 2).sum(axis=0))
		self._start_from_location = start_from_location

	def set_path(self, path):
		self._path = path

	def init(self, sprite, checkpoint=0):
		self._checkpoint = checkpoint
		if self._start_from_location:
			self.set_current_state_from_location(sprite)
		else:
			sprite.set_location(self._path[checkpoint])
			self.set_current_state_from_path()
	
	def cont(self, sprite):
		if self._start_from_location:
			self.set_current_state_from_location(sprite)
		else:
			sprite.set_location(self._path[checkpoint])
			self.set_current_state_from_path()
	
	def get_next_checkpoint_id(self):
		if self._way == PathMotion.Start_to_End:
			return (self._checkpoint + 1) % len(self._path)
		elif self._way == PathMotion.End_to_Start:
			return (self._checkpoint - 1) % len(self._path)

	def set_current_state_from_dir(self, dir):
		if np.abs(dir).sum() == 0:
			id = self._state_name_to_id['rest']
			state = self._indice_states[id]
		else:
			# FIXME : verifier qu'il n'y a pas d'inversion haut/bas
			dot = np.dot(dir, self._directions)
			# (0, 0) direction has been removed
			id = np.argmax(dot) + 1
			state = self._indice_states[id]
		self.change_state(self._current_state, state)

	def set_current_state_from_location(self, sprite):
		n = self.get_next_checkpoint_id()
		d = np.array(self._path[n]) - np.array(sprite.get_location())
		self._current_dir = d
		self.set_current_state_from_dir(d)

	def set_current_state_from_path(self):
		p = self._checkpoint
		n = self.get_next_checkpoint_id()
		d = np.array(self._path[n]) - np.array(self._path[p])
		self._current_dir = d
		self.set_current_state_from_dir(d)

	def update_sprite(self, sprite, dt):
		'''
    Update location and state of the sprite.

    location : old location
    dt : time since last update

		'''
		s = 1
		location = sprite.get_location()
		while s > 0:
			n = self.get_next_checkpoint_id()
			state_name = self._current_state.name
			id = self._state_name_to_id[state_name]
			if id == 0: return
			dir = self._path[n] - location
			dir /= np.sqrt((dir ** 2).sum(axis=0))
			delta = ( dir * dt) * \
				self._speed / 1000.
			new_loc = location + delta
			s = np.dot(self._current_dir, new_loc - self._path[n])
			if s > 0:
				# distance already covered
				dist = np.sqrt(((location - \
						self._path[n]) ** 2).sum())
				location = self._path[n]
				self._checkpoint = n
				self.set_current_state_from_path()
				#remaining time to cover path during this update
				dt -= dist * 1000 / self._speed
		location = new_loc
		sprite.set_location(new_loc)


class KeyboardFullArrowsMotion(Motion):
	def __init__(self, name='sprite', context=None, speed=100.):
		Motion.__init__(self, name, context, speed)
		if context is not None:
			self._register_transitions(context)

	def _register_transitions(self, context):
		states = [State("rest"), State("left"), State("left-up"),
			State("up"), State("right-up"),
			State("right"), State("right-down"),
			State("down"), State("left-down")]
		for state in states: self.add_state(state)
		self.set_initial_state(states[0])

		# left
		signal = (KeyBoardDevice.constants.KEYDOWN,
				KeyBoardDevice.constants.K_LEFT)
		states[0].add_transition(context, signal, states[1])
		signal = (KeyBoardDevice.constants.KEYUP,
				KeyBoardDevice.constants.K_LEFT)
		states[1].add_transition(context, signal, states[0])

		# up
		signal = (KeyBoardDevice.constants.KEYDOWN,
				KeyBoardDevice.constants.K_UP)
		states[0].add_transition(context, signal, states[3])
		signal = (KeyBoardDevice.constants.KEYUP,
				KeyBoardDevice.constants.K_UP)
		states[3].add_transition(context, signal, states[0])

		# right
		signal = (KeyBoardDevice.constants.KEYDOWN,
				KeyBoardDevice.constants.K_RIGHT)
		states[0].add_transition(context, signal, states[5])
		signal = (KeyBoardDevice.constants.KEYUP,
				KeyBoardDevice.constants.K_RIGHT)
		states[5].add_transition(context, signal, states[0])

		# down
		signal = (KeyBoardDevice.constants.KEYDOWN,
				KeyBoardDevice.constants.K_DOWN)
		states[0].add_transition(context, signal, states[7])
		signal = (KeyBoardDevice.constants.KEYUP,
				KeyBoardDevice.constants.K_DOWN)
		states[7].add_transition(context, signal, states[0])

		# FIXME : add diagonal
		# FIXME : norm of diagonal moves must be equal to one
		self._delta_moves = np.array(\
			[[0, -1., -1., 0, 1., 1., 1., 0, -1.],
			[0, 0, -1., -1., -1., 0, 1., 1., 1.]]).T
		self._delta_moves *= self._speed
		self._state_name_to_id = {"rest" : 0, "left" : 1, "left-up" : 2,
				'up' : 3, 'right-up' : 4, 'right' : 5,
				'right-down' : 6, 'down' : 7, 'left-down' : 8}

	def set_context(self, context):
		Motion.set_context(self, context)
		self._register_transitions(context)

	def update_sprite(self, sprite, dt):
		state_name = self._current_state.name
		if state_name == 'rest': return
		id = self._state_name_to_id[state_name]
		delta = (self._delta_moves[id] * dt / 1000.)
		new_loc = sprite.get_location() + delta
		# FIXME: test if new_loc is available
		sprite.set_location(new_loc)


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
		self.set_motion(static_motion)

	def set_motion(self, motion, cont=False):
		if motion.get_context() is None:
			motion.set_context(self.get_context())
		self._motion = motion
		motion.start()
		if cont:
			motion.cont(self)
		else:	motion.init(self)

	def get_motion(self):
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
