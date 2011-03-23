

class Event(object): pass


class SignalEvent(Event):
	def __init__(self, sender, method, signal, signal_data=None):
		self.type = 'signal'
		self.sender = sender
		self.method = method
		self.signal = signal
		self.signal_data = signal_data

	def start(self):
		self.method(self)
