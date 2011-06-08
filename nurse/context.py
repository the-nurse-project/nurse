from state_machine import State, StateMachine
from config import Config

class Context(State):
	def __init__(self, name, is_visible=True, is_active=True,
					_is_receiving_events=True):
		State.__init__(self, name)
		self._visible_data = {}
		self._screens = []
		self._fsm_list = []
		self.is_visible = is_visible
		self.is_active = is_active
		self._is_receiving_events = _is_receiving_events

	def add_fsm(self, fsm):
		self._fsm_list.append(fsm)

	def remove_fsm(self, fsm):
		self._fsm_list.remove(fsm)

	def add_visible_data(self, data, layer=0):
		self._visible_data.setdefault(layer, []).append(data)

	def get_visible_data(self):
		return self._visible_data

	def add_screen(self, screen):
		self._screens.append(screen)

	def display(self):
		for screen in self._screens:
			screen.display_context(self)

	def update(self, dt):
		for fsm in self._fsm_list:
			fsm.update(dt)

	def delegate(self, event):
		self.emit(event.signal, event.signal_data)

	def is_receiving_events(self):
		return self._is_receiving_events

        def set_visible(self, sprite, is_visible, layer=None):
               '''
    set sprite visible or invisible in its parent context
               '''
               if is_visible == False:
                       layers_detected = []    # contains the layers in which the sprite name is found
                       if layer is None:
                               layers = self.get_visible_data().keys()
                               for l in layers:
                                       for obj in self.get_visible_data()[l] :
                                               if obj == sprite :
                                                       layers_detected.append(l)
		       layer = layers_detected[0]
					
                       if len(layers_detected) > 1:
                              raise Exception('Different sprites match name \'%s\', must specify layer'\
                                      %sprite.name )
						
                       self.get_visible_data()[layer].remove(obj)
               else :
                       self.add_visible_data(sprite, sprite._layer)

class ContextManager(StateMachine):
	def __init__(self):
		StateMachine.__init__(self, 'Context Manager')
		signal = '__all__'
		Config.get_keyboard_device().connect(signal, self,
						asynchronous=False)

	def display(self):
		Config.get_graphic_engine().clean()
		for context in self._possible_states.values():
			if context.is_visible:
				context.display()
		Config.get_graphic_engine().flip()

	def update(self, dt):
		for context in self._possible_states.values():
			if context.is_active:
				context.update(dt)

	# slots
	def receive_events(self, event):
		# - try to modify the current context
		# - then notify observers
		try:
			self._current_state.on_transition(event)
		except KeyError:
			for context in self._possible_states.values():
				if context.is_receiving_events():
					context.delegate(event)
