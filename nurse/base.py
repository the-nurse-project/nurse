from events import SignalEvent

''' A low-level class for signal transmission between objects.
.. module:: base
   :platform: Unix
      :synopsis: A useful module indeed.

.. moduleauthor:: Matthieu Perrot <matthieu.perrot@gmail.com>

'''

class Object(object):

	def __init__(self, name):
		self.name = name
		self._sync_connections = {'__all__' : []}		
		self._async_connections = {'__all__' : []}		

	def set_property(self, name, value):
		'''
    Assigns an attribute to the object.

    Parameters:
    
    name : str
    value : dtype

		'''

		self.__setattr__(name, value)

	def is_receiving_events(self):
		'''
    For now, returns True.

    Returns:
    
    True

		'''

		return True

	def connect(self, signal, receiver, slot="receive_events",
						asynchronous=True):
		'''
    Mimics Qt signal/slot connection. 

    Parameters:
  
    signal : any pickable object        
    	If signal is equal to '__all__' the slot function will be called for 
	any signal.
    receiver : Object 
    	Destination object.
    slot : str
    	Name of the function to call on the receiver.
    asynchronous : bool
    	True if the the slot is queued in the eventloop.
	False if the slot is called directly during the emit call.

		'''

		connection = (receiver, slot)
		if asynchronous:
			connections = self._async_connections
		else:	connections = self._sync_connections
		connections.setdefault(signal, []).append(connection)

	def disconnect(self, signal, receiver, slot="receive_events",
						asynchronous=True):
		'''
    Disconnects the object from the given signal/receiver/slot binding.

    Parameters:

    signal : any pickable object
    receiver : Object
    slot : str
    asynchronous : bool

		'''

                connection = (receiver, slot)
                if asynchronous:
                        connections = self._async_connections
                else:   connections = self._sync_connections
                connections[signal].remove(connection)

	def emit(self, signal, signal_data=None):
		'''
   Emits a signal and associated signal data if provided. For instance, 
   signal data can help identifying between which states of a context a 
   transition is happening.

   Parameters:
   
   signal : any pickable object
   signal_data : any pickable object

   See Also:

   :func:`nurse.state_machine.change_state`

		'''

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
			event = SignalEvent(self, receiver, slot,
						signal, signal_data)
			event.start()

		connections = [(receiver, slot) \
			for (receiver, slot) in async_connections
			if receiver.is_receiving_events()]

		from config import Config # FIXME : move somewhere else
		event_loop = Config.get_event_loop()
		for (receiver, slot) in connections:
			event = SignalEvent(self, receiver, slot,
						signal, signal_data)
			event_loop.add_event(event)

	def call_slot(self, slot, event):
		'''
    This function is the uniq valid entry point to resolve any slot call.
    It could be reimplemented by class children to add features around the
    method call.

    slot:   string name of the function to be called on self.
    event:  Event instance (pass as parameter to the slot method).
		'''
		method = self.__getattribute__(slot)
		method(event)


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


universe = Object('universe')
