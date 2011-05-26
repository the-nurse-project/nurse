

class Event(object): pass


class SignalEvent(Event):
	def __init__(self, sender, receiver, slot, signal, signal_data=None):
		self.type = 'signal'
		self.sender = sender
		self.receiver = receiver 
		self.slot = slot 
		self.signal = signal
		self.signal_data = signal_data

	def start(self):
		self.receiver.call_slot(self.slot, self)
