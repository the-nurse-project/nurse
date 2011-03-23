from events import SignalEvent

class Object(object):
	def __init__(self, name):
		self.name = name
		self._sync_connections = {'__all__' : []}		
		self._async_connections = {'__all__' : []}		

	def set_property(self, name, value):
		self.__setattr__(name, value)

	def is_receiving_events(self):
		return True

	def connect(self, signal, receiver, slot="receive_events",
						asynchronous=True):
		'''
    mimic qt signal/slot connection

    signal:        any pickable object. If signal is equal to __all__ the slot
                   function will be called for any signal.
    receiver:      destination object.
    slot:          name of the function to call on the receiver.
    asynchronous:  true if the the slot is queued in the eventloop.
                   false if the slot is called directly during the emit call.
		'''
		connection = (receiver, slot)
		if asynchronous:
			connections = self._async_connections
		else:	connections = self._sync_connections
		connections.setdefault(signal, []).append(connection)

	def disconnect(self, signal, receiver, slot="receive_events",
						asynchronous=True):
		connection = (receiver, slot, asynchronous)
		connections = self._connections[signal]
		del connections[connections.index(connection)]

	def emit(self, signal, signal_data=None):
		try:
			async_connections = self._async_connections[signal]
		except KeyError:
			async_connections = []
		async_connections += self._async_connections['__all__']
		try:
			sync_connections = self._sync_connections[signal]
		except KeyError:
			sync_connections = []
		sync_connections += self._sync_connections['__all__']

		# batch active slots :
		#   done in 2 passes to avoid domino effect if some observers
		#   is_receiving_events status change after a first observer
		#   receive a signal.
		connections = [(receiver, slot) \
			for (receiver, slot) in sync_connections
			if receiver.is_receiving_events()]

		for (receiver, slot) in connections:
			method = receiver.__getattribute__(slot)
			event = SignalEvent(self, method, signal, signal_data)
			method(event)

		connections = [(receiver, slot) \
			for (receiver, slot) in async_connections
			if receiver.is_receiving_events()]

		from config import Config # FIXME : move somewhere else
		event_loop = Config.get_event_loop()
		for (receiver, slot) in connections:
			method = receiver.__getattribute__(slot)
			event = SignalEvent(self, method, signal, signal_data)
			event_loop.add_event(event)


universe = Object('universe')
