from base import Object
from config import Config


class State(Object):
	def __init__(self, name):
		Object.__init__(self, name)
		self._fsm = None
		self._assign_properties = []
		self._transitions = {}

	def add_transition(self, sender, signal, state,
			src_prop={}, dst_prop={}, asynchronous=True):
		sender.connect(signal, self, "on_transition", asynchronous)
		self._transitions[signal] = (sender, state, src_prop, dst_prop)

	def assign_property(self, obj, name, value):
		self._assign_properties.append((obj, name, value))

	def remove_transition(self, transition):
		del self._transitions[transition]
		self._initial_state = state

	def is_receiving_events(self):
		return self._fsm._current_state == self

	# slots
	def on_entered(self):
		for (obj, name, value) in self._assign_properties:
			obj.set_property(name, value)
		self.emit("entered")

	def on_exited(self):
		self.emit("exited")

	def on_transition(self, event):
		sender, state, src_prop, dst_prop = \
			self._transitions[event.signal]
		self._fsm.change_state(self, state, src_prop, dst_prop)


class StateMachine(State):
	START = 0
	STOP = 1
	def __init__(self, name='state machine', context=None):
		State.__init__(self, name)
		self._initial_state = None
		self._possible_states = {}
		self._current_state = None
		if context is not None: context.add_fsm(self)
		self._context = context

	def update(self, dt):
		'''
    The event loop periodically call this method on state machines registered
    to an active context.

    Parameters:
  
    dt : float
        delta of time (in ms) since the last call.
		'''
		pass

	def get_context(self):
		return self._context

	def set_context(self, context):
		old_context = self._context
		if old_context is not None: old_context.remove_fsm(self)
		self._context = context
		self._context.add_fsm(self)

	def set_initial_state(self, state):
		if state not in self._possible_states.values():
			raise ValueError('unknown initial state')
		self._initial_state = state

	def add_state(self, state):
		self._possible_states[state.name] = state
		state._fsm = self

	def change_state(self, src, dst, src_prop={}, dst_prop={}):
		if src != self._current_state: return
		if self._current_state is not None:
			self._current_state.on_exited()
		self._current_state = dst 
		if self._current_state is not None:
			self._current_state.on_entered()
		for k, v in src_prop.items(): src.set_property(k, v)
		for k, v in dst_prop.items(): dst.set_property(k, v)
		self.emit("state_changed", (src, dst))

	def start(self):
		if self._initial_state is None:
			default_state = State('__default__')
			self.add_state(default_state)
			self._initial_state = default_state
		self._current_state = self._initial_state
		self._current_state.on_entered()
		self.status = StateMachine.START
		self.emit("started")

	def stop(self):
		self.status = StateMachine.STOP
		self.emit("stopped")

	def is_receiving_events(self):
		return True

	# slots
	def on_entry(self):
		self.start()

	def on_exit(self):
		self.stop()
