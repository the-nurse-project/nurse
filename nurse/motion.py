import numpy as np

from base import Object
from state_machine import StateMachine, State
from config import Config
from backends import KeyBoardDevice


class Motion(StateMachine):
	def __init__(self, name='motion', context=None, speed=100.):
		'''
    speed: speed in world-coordinate metric per seconds
		'''
		StateMachine.__init__(self, name, context)
		self._speed = speed

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
