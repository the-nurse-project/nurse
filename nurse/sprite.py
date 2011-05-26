import numpy as np

from state_machine import StateMachine, State
from config import Config
from backends import KeyBoardDevice


class Sprite(StateMachine):
	def __init__(self, name='sprite', context=None, layer=1, speed=100.):
		'''
    name:  name of the sprite
    layer: (default: 1 since 0 is reserved for background)
    speed: speed in world-coordinate metric per seconds
		'''
		StateMachine.__init__(self, name, context)
		if context is None: context = Config.get_default_context()
		context.add_visible_data(self, layer)
		self._current_frame_id = 0
		self._frames = {}
		self._frames_center_location = {}
		self._refresh_delay = {}
		self._location = np.zeros(2)
		self._speed = speed

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
		self._size = np.array([0., 0.])
		if isinstance(center_location, str):
			for img in self._frames[state]:
				width, height = img.get_size()
				if width > self._size[0]:
					self._size[0] = width
				if height > self._size[1]:
					self._size[1] = height
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

	def update(self, dt):
		'''
    Update sprite location (in world coordinates) according to its
    control state and current active frame
		'''
		raise NotImplementedError

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

	def bounding_box(self):
		return (self._location[0] - self._bb_center[0], 
			self._location[1] - self._bb_center[1], 
			self._size[0], self._size[1])


class MovingSprite(Sprite):
	Start_to_End = 0
	End_to_Start = 1
	def __init__(self, name='moving sprite', context=None,
					layer=2, speed=100.):
		'''
    path : list of world coordinates
		'''
		Sprite.__init__(self, name, context, layer, speed)
		if context is None: context = Config.get_default_context()
		self._path = None
		self._way = MovingSprite.Start_to_End
		self._indice_states = [\
			State("rest"), State("left"), State("left-up"),
			State("up"), State("right-up"),
			State("right"), State("right-down"),
			State("down"), State("left-down")]
		self._state_name_to_id = {"rest" : 0, "left" : 1, "left-up" : 2,
				'up' : 3, 'right-up' : 4, 'right' : 5,
				'right-down' : 6, 'down' : 7, 'left-down' : 8}
		for state in self._indice_states: self.add_state(state)
		self.set_initial_state(self._indice_states[0])
		self._checkpoint = 0
		self._directions = np.array([\
			[-1., -1., 0, 1., 1., 1., 0, -1.],
			[0, -1., -1., -1., 0, 1., 1., 1.]])
		self._directions /= np.sqrt((self._directions ** 2).sum(axis=0))

	def set_path(self, path):
		self._path = path
		self.set_current_state_from_path()
		self.set_initial_state(self._current_state)
		self.set_location(self._path[0])

	def get_next_checkpoint_id(self):
		if self._way == MovingSprite.Start_to_End:
			return (self._checkpoint + 1) % len(self._path)
		elif self._way == MovingSprite.End_to_Start:
			return (self._checkpoint + 1) % len(self._path)

	def set_current_state_from_path(self):
		p = self._checkpoint
		n = self.get_next_checkpoint_id()
		d = np.array(self._path[n]) - np.array(self._path[p])
		self._current_dir = d
		if np.abs(d).sum() == 0:
			id = self._state_name_to_id['rest']
			state = self._indice_states[id]
		else:
			# FIXME : verifier qu'il n'y a pas d'inversion haut/bas
			dot = np.dot(d, self._directions)
			# (0, 0) direction has been removed
			id = np.argmax(dot) + 1
			state = self._indice_states[id]
		self.change_state(self._current_state, state)

	def update(self, dt):
		'''
    Update location and state of the sprite.

    dt : time since last update
		'''
		# FIXME: test if new_loc is available
		s = 1
		while s > 0:
			p = self._checkpoint
			n = self.get_next_checkpoint_id()
			state_name = self._current_state.name
			id = self._state_name_to_id[state_name]
			if id == 0: return
			delta = (self._directions.T[id - 1] * dt) * \
				self._speed / 1000.
			new_loc = self._location + delta
			s = np.dot(self._current_dir, new_loc - self._path[n])
			if s > 0:
				# distance already covered
				dist = np.sqrt(((self._location - \
						self._path[n]) ** 2).sum())
				self._location = self._path[n]
				self._checkpoint = n
				self.set_current_state_from_path()
				#remaining time to cover path during this update
				dt -= dist * 1000 / self._speed
		self._location = new_loc
		self.emit("location_changed", new_loc)


class Player(Sprite):
	def __init__(self, name='sprite', context=None,
				layer=2, speed=100.):
		Sprite.__init__(self, name, context, layer, speed)
		if context is None: context = Config.get_default_context()
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

	def update(self, dt):
		state_name = self._current_state.name
		if state_name == 'rest': return
		id = self._state_name_to_id[state_name]
		delta = (self._delta_moves[id] * dt / 1000.)
		new_loc = self._location + delta
		# FIXME: test if new_loc is available
		self._location = new_loc
		self.emit("location_changed", new_loc)


class StaticSprite(Sprite):
	def __init__(self, name, context, layer=0, imgname=None):
		Sprite.__init__(self, name, context, layer)
		self.load_frames_from_filenames('__default__',
					[imgname], 'centered', 1)

	def get_frame_infos(self, time):
		state = '__default__'
		frames = self._frames[state]
		frames_center_location = self._frames_center_location[state]
		return frames[0], frames_center_location[0]

	def update(self, dt):
		pass


class UniformLayer(Sprite):
	def __init__(self, name, context, layer=2, size=None,
			shift=(0, 0), color=(0, 0, 0), alpha=128):
		Sprite.__init__(self, name, context, layer)
		gfx = Config.get_graphic_engine()
		self._surface = gfx.get_uniform_surface(shift, size,
							color, alpha)
		self._center = np.array(self._surface.get_size()) / 2.
		self._size = size
		self._bb_center = self._center.copy()
		self.set_location(shift)

	def get_frame_infos(self, time):
		return self._surface, self._center

	def update(self, dt):
		pass


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
