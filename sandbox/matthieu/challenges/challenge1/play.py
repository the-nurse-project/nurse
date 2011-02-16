import os, sys
import numpy as np
import pygame

UPDATEEVENT = pygame.USEREVENT + 1

#-------------------------------------------------------------------------------
class Object(object):
	def set_property(self, name, value):
		self.__setattr__(name, value)


class Universe(Object):
	def __init__(self, update_freq=10):
		'''
    update_freq: update frequency
		'''
		Object.__init__(self)
		self._update_delay = int(1000 / update_freq)
		pygame.time.set_timer(UPDATEEVENT, self._update_delay)
		self._pending_events = []
		self._fsm_list = []
		self._visible_data = {}

	def add_fsm(self, fsm):
		self._fsm_list.append(fsm)

	def add_sdl_device(self, sdl_device):
		self.sdl_device = sdl_device
		signal = (UPDATEEVENT, None)
		sdl_device.attach(self, signal)

	def add_event(self, event):
		self._pending_events.append(event)

	def get_events(self):
		try:
			yield self._pending_events.pop()
		except IndexError: pass

	def read_events(self):
		#for e in self.get_events():
		if len(self._pending_events) != 0:
			e = self._pending_events.pop()
			e.start()
		self.sdl_device.read_events()

	def receive_event(self, event):
		if event.type == 'update':
			for fsm in self._fsm_list:
				fsm.update()

	def add_visible_data(self, data, layer=0):
		self._visible_data.setdefault(layer, []).append(data)

	def get_visible_data(self):
		return self._visible_data


Object.universe = Universe(15)


class Event(Object):
	def __init__(self, sender, observer):
		Object.__init__(self)
		self.sender = sender
		self.observer = observer

	def start(self):
		self.observer.receive_event(self)


class SignalEvent(Event):
	def __init__(self, sender, observer, signal):
		Event.__init__(self, sender, observer)
		self.signal = signal
		self.type = 'signal'


class UpdateEvent(Event):
	def __init__(self, sender, observer):
		Event.__init__(self, sender, observer)
		self.type = 'update'


class Observable(Object):
	def __init__(self):
		Object.__init__(self)
		self._observers = {}

	def attach(self, observer, signal):
		if not observer in self._observers:
			self._observers.setdefault(signal, []).append(observer)

	def detach(self, observer, signal):
		try:
			self._observers[signal].remove(observer)
		except ValueError:
			pass

	def notify(self, signal, asynchronous=True):
		# FIXME : asynchronisme a gerer du cote de l'observer plutot
		if not self._observers.has_key(signal): return
		if asynchronous:
			for observer in self._observers[signal]:
				event = SignalEvent(self, observer, signal)
				Object.universe.add_event(event)
		else:
			for observer in self._observers[signal]:
				event = SignalEvent(self, observer, signal)
				event.start()


class State(Observable):
	def __init__(self, name, parent=None):
		Observable.__init__(self)
		# FIXME : parent/child/hiearchical state not handle yet
		self._name = name
		self._fsm = None
		self._assign_properties = []
		self._transitions = []
		self._initial_state = None
		self._updates = {}
		if parent is not None:
			parent._initial_state = self

	def get_name(self):
		return self._name

	def add_transition(self, sender, signal, state):	
		sender.attach(self, signal)
		self._updates[signal] = (sender, state)

	def assign_property(self, obj, name, value):
		self._assign_properties.append((obj, name, value))

	def initial_state(self):
		return self._initial_state

	def remove_transition(self, transition):
		self._transitions.remove(transition)

	def set_initial_state(self, state):
		self._initial_state = state

	def receive_event(self, event):
		sender, state = self._updates[event.signal]
		self._fsm.change_state(self, state)

	def _signal_entered(self):
		for (obj, name, value) in self._assign_properties:
			obj.set_property(name, value)
		self.on_entry()
		self.notify("entered")
		# print "State : ", self._name

	def _signal_exited(self):
		self.on_exit()
		self.notify("exited")

	def on_entry(self): pass

	def on_exit(self): pass

	# signals : entered, exited


class StateMachine(State):
	START = 0
	STOP = 1
	def __init__(self, name=None):
		State.__init__(self, name)
		self._initial_state = None
		self._possible_states = {}
		self._current_state = None
		self.universe.add_fsm(self)

	def set_initial_state(self, state):
		if state not in self._possible_states.values():
			raise ValueError('unknown initial state')
		self._initial_state = state

	def add_state(self, state):
		self._possible_states[state.get_name()] = state
		state._fsm = self

	def change_state(self, src, dst):
		if src != self._current_state: return
		self._current_state._signal_exited()
		self._current_state = dst 
		self._current_state._signal_entered()

	def finished(self):
		pass

	def start(self):
		if self._initial_state is None:
			default_state = State('__default__')
			self.add_state(default_state)
			self._initial_state = default_state
		self._current_state = self._initial_state
		self._current_state._signal_entered()
		self.status = StateMachine.START
		self.notify("started")

	def stop(self):
		self.status = StateMachine.STOP
		self.notify("stopped")

	def on_entry(self):
		self.start()

	def on_exit(self):
		self.stop()

	def post_event(self): pass #FIXME



class Sprite(StateMachine):
	def __init__(self, name=None, layer=1):
		'''
    name:  name of the sprite
    layer: (default: 1 since 0 is reserved for background)
		'''
		StateMachine.__init__(self, name)
		self._current_frame_id = 0
		self._frames = {}
		self._frames_center_location = {}
		self._refresh_delay = {}
		self._location = np.zeros(2)
		self.universe.add_visible_data(self, layer)
		self._previous_time = pygame.time.get_ticks()

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
		self._frames[state] = [pygame.image.load(fname).convert() \
					for fname in frames_fnames]
		alpha_color = (0xff, 0, 0xff)
		flags = pygame.constants.SRCCOLORKEY | pygame.constants.RLEACCEL
		for img in self._frames[state]:
			img.set_colorkey(alpha_color, flags)
		self._refresh_delay[state] = int(1000 / fps)
		loc = []
		if isinstance(center_location, str):
			if center_location == 'centered':
				for img in self._frames[state]:
					loc.append(np.array(img.get_size()) /2.)
			elif center_location == 'centered_bottom':
				for img in self._frames[state]:
					width, height = img.get_size()
					loc.append(np.array([width/2., height]))
		elif isinstance(center_location, list):
			loc = center_location
		else:	loc = [center_location] * len(self._frames[state])
		self._frames_center_location[state] = loc

	def get_frame_infos(self, time):
		'''
    Return frame infos for a given time : image, center location
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

	def update(self):
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



class Player(Sprite):
	def __init__(self, name=None, layer=2):
		Sprite.__init__(self, name, layer)
		states = [State("lasy"), State("left"), State("left-up"),
			State("up"), State("right-up"),
			State("right"), State("right-down"),
			State("down"), State("left-down")]
		for state in states: self.add_state(state)
		self.set_initial_state(states[0])

		sdl_device = Object.universe.sdl_device
	
		# left
		signal = (pygame.constants.KEYDOWN, pygame.constants.K_LEFT)
		states[0].add_transition(sdl_device, signal, states[1])
		signal = (pygame.constants.KEYUP, pygame.constants.K_LEFT)
		states[1].add_transition(sdl_device, signal, states[0])

		# up
		signal = (pygame.constants.KEYDOWN, pygame.constants.K_UP)
		states[0].add_transition(sdl_device, signal, states[3])
		signal = (pygame.constants.KEYUP, pygame.constants.K_UP)
		states[3].add_transition(sdl_device, signal, states[0])

		# right
		signal = (pygame.constants.KEYDOWN, pygame.constants.K_RIGHT)
		states[0].add_transition(sdl_device, signal, states[5])
		signal = (pygame.constants.KEYUP, pygame.constants.K_RIGHT)
		states[5].add_transition(sdl_device, signal, states[0])

		# down
		signal = (pygame.constants.KEYDOWN, pygame.constants.K_DOWN)
		states[0].add_transition(sdl_device, signal, states[7])
		signal = (pygame.constants.KEYUP, pygame.constants.K_DOWN)
		states[7].add_transition(sdl_device, signal, states[0])

		# FIXME : add diagonal
		# FIXME : value of delta in pixels
		delta = 10
		self._delta_moves = np.array(\
			[[0, -delta, -delta, 0, delta, delta, delta, 0, -delta],
			[0, 0, -delta, -delta, -delta, 0, delta, delta, delta]\
			]).T
		self._state_name_to_id = {"lasy" : 0, "left" : 1, "left-up" : 2,
				'up' : 3, 'right-up' : 4, 'right' : 5,
				'right-down' : 6, 'down' : 7, 'left-down' : 8}

	def update(self):
		state_name = self._current_state.get_name()
		time = pygame.time.get_ticks()
		delta = (time - self._previous_time)
		f = float(delta) / Object.universe._update_delay
		self._previous_time = time
		if state_name == 'lasy': return
		id = self._state_name_to_id[state_name]
		new_loc = self._location + self._delta_moves[id] * f
		# FIXME: test if new_loc is available
		self._location = new_loc
		self.notify("location_changed", asynchronous=False)



class Background(Sprite):
	def __init__(self, name=None, layer=0):
		Sprite.__init__(self, name, layer)

	def update(self):
		# FIXME : on pourrait peut-etre eviter cet appel inutile
		# en creant une liste de sprites a updater
		pass

#-------------------------------------------------------------------------------
class SDL_device(State):
	def __init__(self):
		State.__init__(self, "SDL device")

	def read_events(self):
		# FIXME : remove specific key handling
		# FIXME : handle diagonal sprite displacement: LEFT + UP, ...
		# for event in pygame.event.get():
		#if 1:
			event = pygame.event.poll()
			if (event.type == 0): return
			keystate = pygame.key.get_pressed()
			if (event.type == pygame.constants.QUIT): sys.exit(0)
			if (event.type == pygame.constants.KEYDOWN):
				keymap = pygame.key.get_pressed()
				if keymap[pygame.constants.K_q] or \
					keymap[pygame.constants.K_ESCAPE]:
					sys.exit(0)
			if event.type == UPDATEEVENT:
				event = UpdateEvent(self, Object.universe)
				Object.universe.add_event(event)
			# filter some events
			elif event.type not in [pygame.constants.KEYDOWN,\
					pygame.constants.KEYUP]: return #continue
			else:	self.notify((event.type, event.key))
			# print event


#-------------------------------------------------------------------------------
class Screen(Object):
	def __init__(self, geometry, focus, focus_on=None, fps=25):
		'''
    geometry:   geometry of the screen: tuple (x, y, w, h):
                x: x position of the bottom left border in screen coordinates
                y: y position of the bottom left border in screen coordinates
                w: width of the screen in pixels
                h: height of the screen in pixels
    focus:      position in world coordinates on which the screen is focused
                (center of the screen).
    focus_on:   follow location of the given object (call get_location() func).
    fps:        number of frames per second (must be < 100)
		'''
		if fps > 100: raise RunTimeError("fps number must be < 100.")
		self._x, self._y, self._width, self._height = geometry
		self.set_focus(focus)
		if focus_on is not None:
			focus_on.attach(self, "location_changed")
		self._refresh_delay = int(1000 / fps) # delay in milliseconds
		self._previous_time = pygame.time.get_ticks()
		self.dst_pos = None

	def set_focus(self, focus):
		self._shift = np.array([self._x + self._width / 2,
					self._y + self._height / 2]) - focus
		self._focus = focus

	def display(self):
		time = pygame.time.get_ticks()
		delta = time - self._previous_time 
		if delta < self._refresh_delay: return
		# print "loop = ", float(delta) / self._refresh_delay
		Screen.sdl_screen2.fill((0, 0, 0))
		data = Object.universe.get_visible_data()
		for layer, objects in data.items(): # from bg to fg
			for obj in objects:
				self.display_object(obj)
		self._previous_time = time
		Screen.sdl_screen.blit(Screen.sdl_screen2, (0, 0))
		pygame.display.flip()
	
	def display_object(self, obj):
		time = pygame.time.get_ticks()
		frame, center = obj.get_frame_infos(time)
		if frame is None: return
		dst_pos = self._shift + obj.get_location() - center
		src_rect = None # pygame.Rect(x, y, w, h) # FIXME
		#if obj._name == 'perso':
		#	if self.dst_pos is None:
		#		self.dst_pos = dst_pos
		#	elif (self.dst_pos != dst_pos).any():
		#		print "pos = ", dst_pos
		#		self.dst_pos = dst_pos
		Screen.sdl_screen2.blit(frame, dst_pos, src_rect)

	def receive_event(self, event):
		if event.type == 'signal':
			if event.signal == 'location_changed':
				self.set_focus(event.sender.get_location())


#-------------------------------------------------------------------------------
def create_bg():
	fsm = Background('hospital', layer=0)
	fsm.load_frames_from_filenames('__default__', ['pix2/hopital.png'],
						'centered', 1)
	fsm.set_location(np.array([-100, -100]))
	fsm.start()
	return fsm

def create_perso():
	fsm = Player("perso", layer=2)
	fsm.load_frames_from_filenames('__default__', ['pix2/perso.png'],
						'centered_bottom', 1)
	fsm.set_location(np.array([-260, -140]))
	fsm.start()
	return fsm

#-------------------------------------------------------------------------------
def main():
	pygame.init()
	# WARNING: key event are repeated under NX
	pygame.key.set_repeat() # prevent key repetition
	resolution = 800, 600
	flags = pygame.constants.DOUBLEBUF | pygame.constants.HWSURFACE | \
		pygame.constants.HWACCEL # | pygame.FULLSCREEN  
	sdl_screen = pygame.display.set_mode(resolution, flags)
	Screen.sdl_screen = sdl_screen
	Screen.sdl_screen2 = sdl_screen.copy()
	# print sdl_screen
	#sys.exit(1)

	#FIXME : find another way to add the device
	Object.universe.add_sdl_device(SDL_device())

	# game
	# screen = Screen((10, 10, 300, 300), (-100, -100))
	bg = create_bg()
	perso = create_perso()
	screen = Screen((0, 0, resolution[0], resolution[1]),
				# bg.get_location(), fps=30)
				#perso.get_location(), perso, fps=30)
				perso.get_location(), fps=30)
	# event loop
	while 1:
		StateMachine.universe.read_events()
		screen.display()


if __name__ == "__main__" : main()
#-------------------------------------------------------------------------------
# Notes:
# 1) PNJ : mise a jour automatique des coordonnees (x,y) selon un chemin.
#   timer/temps et frames a prendre en compte.
#
# 2) PJ : gerer les shifts de coordonnees (x,y) +=/-= pour deplacer le sprite en
#   fonction des touches du clavier. La gestion du temps (timer ?) est a prendre
#   en compte pour bien gerer les frames
# 3) gerer 2 touches actives en meme temps : Left et Up par ex (un seul event actif avec SDL)
