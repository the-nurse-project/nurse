import os, sys
import numpy as np
import pygame

fps = 60.

#-------------------------------------------------------------------------------
class Object(object):
	def set_property(self, name, value):
		self.__setattr__(name, value)


class Universe(Object):
	def __init__(self):
		Object.__init__(self)
		self._pending_events = []
		self._fsm_list = []
		self._visible_data = {}

	def add_fsm(self, fsm):
		self._fsm_list.append(fsm)

	def add_sdl_device(self, sdl_device):
		self.sdl_device = sdl_device

	def add_event(self, event):
		self._pending_events.append(event)

	def get_events(self):
		try:
			yield self._pending_events.pop()
		except IndexError: pass

	def read_events(self):
		if len(self._pending_events) != 0:
			e = self._pending_events.pop()
			e.start()
		self.sdl_device.read_events()

	def receive_event(self, event):
		pass

	def update(self, dt):
		for fsm in self._fsm_list:
			fsm.update(dt)

	def add_visible_data(self, data, layer=0):
		self._visible_data.setdefault(layer, []).append(data)

	def get_visible_data(self):
		return self._visible_data


Object.universe = Universe()


class Event(Object):
	def __init__(self, sender, observers):
		Object.__init__(self)
		self.sender = sender
		self.observers = observers

	def start(self):
		for observer in self.observers:
			observer.receive_event(self)


class SignalEvent(Event):
	def __init__(self, sender, observers, signal):
		Event.__init__(self, sender, observers)
		self.signal = signal
		self.type = 'signal'


class UpdateEvent(Event):
	def __init__(self, sender, observers):
		Event.__init__(self, sender, observers)
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

	def notify(self, signal, batch=True, asynchronous=True):
		# FIXME : asynchronisme a gerer du cote de l'observer plutot
		# FIXME : recevoir un signal non attendu est-il normal ?
		if not self._observers.has_key(signal): return
		observers = self._observers[signal]
		if asynchronous:
			if batch is True:
				event = SignalEvent(self, observers, signal)
				Object.universe.add_event(event)
			else:
				for observer in observers:
					event = SignalEvent(self,
							[observer], signal)
					Object.universe.add_event(event)
		else:
			# for synchronoous events : data are batched
			event = SignalEvent(self, observers, signal)
			event.start()


class State(Observable):
	def __init__(self, name, parent=None):
		Observable.__init__(self)
		# FIXME : parent/child/hiearchical state not handle yet
		self._name = name
		self._fsm = None
		self._assign_properties = []
		self._transitions = []
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

	def remove_transition(self, transition):
		self._transitions.remove(transition)

		self._initial_state = state

	def receive_event(self, event):
		sender, state = self._updates[event.signal]
		self._fsm.change_state(self, state)

	def _signal_entered(self):
		for (obj, name, value) in self._assign_properties:
			obj.set_property(name, value)
		self.on_entry()
		self.notify("entered")

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
		if self._current_state is not None:
			self._current_state._signal_exited()
		self._current_state = dst 
		if self._current_state is not None:
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
	def __init__(self, name=None, layer=1, speed=100.):
		'''
    name:  name of the sprite
    layer: (default: 1 since 0 is reserved for background)
    speed: speed in world-coordinate metric per seconds
		'''
		StateMachine.__init__(self, name)
		self._current_frame_id = 0
		self._frames = {}
		self._frames_center_location = {}
		self._refresh_delay = {}
		self._location = np.zeros(2)
		self.universe.add_visible_data(self, layer)
		self._speed = speed
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
		self._frames[state] = [pygame.image.load(fname) \
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


class MovingSprite(Sprite):
	Start_to_End = 0
	End_to_Start = 1
	def __init__(self, name=None, layer=2, speed=100.):
		'''
    path : list of world coordinates
		'''
		Sprite.__init__(self, name, layer, speed)
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
			state = 'rest'
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
			state_name = self._current_state.get_name()
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
		self.notify("location_changed", asynchronous=False)


class Player(Sprite):
	def __init__(self, name=None, layer=2, speed=100.):
		Sprite.__init__(self, name, layer, speed)
		states = [State("rest"), State("left"), State("left-up"),
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
		# FIXME : norm of diagonal moves must be equal to one
		self._delta_moves = np.array(\
			[[0, -1., -1., 0, 1., 1., 1., 0, -1.],
			[0, 0, -1., -1., -1., 0, 1., 1., 1.]]).T
		self._delta_moves *= self._speed
		self._state_name_to_id = {"rest" : 0, "left" : 1, "left-up" : 2,
				'up' : 3, 'right-up' : 4, 'right' : 5,
				'right-down' : 6, 'down' : 7, 'left-down' : 8}

	def update(self, dt):
		state_name = self._current_state.get_name()
		# time = pygame.time.get_ticks()
		# delta = (time - self._previous_time)
		# f = float(delta) / Object.universe._update_delay
		# self._previous_time = time
		if state_name == 'rest': return
		id = self._state_name_to_id[state_name]
		delta = (self._delta_moves[id] * dt / 1000.)
		# new_loc = self._location + self._delta_moves[id] * f
		new_loc = self._location + delta
		# FIXME: test if new_loc is available
		self._location = new_loc
		self.notify("location_changed", asynchronous=False)



class Background(Sprite):
	def __init__(self, name=None, layer=0):
		Sprite.__init__(self, name, layer)

	def update(self, dt):
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
				elif keymap[pygame.constants.K_f]:
					pygame.display.toggle_fullscreen()
			# filter some events
			if event.type not in [pygame.constants.KEYDOWN,\
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
		Screen.sdl_screen.fill((0, 0, 0))
		data = Object.universe.get_visible_data()
		for layer, objects in data.items(): # from bg to fg
			for obj in objects:
				self.display_object(obj)
		self._previous_time = time
	
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
		Screen.sdl_screen.blit(frame, dst_pos, src_rect)

	def receive_event(self, event):
		if event.type == 'signal':
			if event.signal == 'location_changed':
				self.set_focus(event.sender.get_location())


#-------------------------------------------------------------------------------
def create_bg():
	fsm = Background('hospital', layer=0)
	fsm.load_frames_from_filenames('__default__', ['pix/hopital.png'],
						'centered', 1)
	fsm.set_location(np.array([-100, -100]))
	fsm.start()
	return fsm

def create_player():
	fsm = Player("player", layer=2, speed=120.)
	fsm.load_frames_from_filenames('__default__', ['pix/perso.png'],
						'centered_bottom', 1)
	fsm.set_location(np.array([-260, -140]))
	fsm.start()
	return fsm

def create_nurse():
	fsm = MovingSprite("nurse", layer=2, speed=180.)
	fsm.load_frames_from_filenames('__default__', ['pix/infirmiere.png'],
							'centered_bottom', 1)

	p1 = [40, -200]
	p2 = [140, -200]
	p3 = [140, 50]
	p4 = [-400, 50]
	p5 = [200, 50]
	path = np.array([p1, p2, p3, p4, p5, p3, p2])
	fsm.set_path(path)
	fsm.start()
	return fsm



#-------------------------------------------------------------------------------
def main():
	pygame.init()
	pygame.font.init()

	# WARNING: key event are repeated under NX
	pygame.key.set_repeat() # prevent key repetition
	resolution = 800, 600
	flags = pygame.constants.DOUBLEBUF | pygame.constants.HWSURFACE | \
		pygame.constants.HWACCEL # | pygame.FULLSCREEN  
	sdl_screen = pygame.display.set_mode(resolution, flags)
	Screen.sdl_screen = sdl_screen

	#FIXME : find another way to add the device
	Object.universe.add_sdl_device(SDL_device())

	# game
	bg = create_bg()
	player = create_player()
	nurse = create_nurse()
	screen = Screen((0, 0, resolution[0], resolution[1]),
				# bg.get_location(), fps=30)
				player.get_location(), player, fps=30)
				# player.get_location(), fps=30)

	font = pygame.font.Font(None, 40)
	clock = pygame.time.Clock()
	previous_time = pygame.time.get_ticks()

	# event loop
	while 1:
		StateMachine.universe.read_events()
		screen.display()
		time = pygame.time.get_ticks()
		dt = time - previous_time
		if dt < (1000. / fps): continue
		clock.tick()
		previous_time = time
		Object.universe.update(dt)
		true_fps = clock.get_fps()
		text = font.render(str(true_fps), True,
			(255, 255, 255), (0, 0, 0))
		# Screen.sdl_screen.blit(text, (0, resolution[1]))
		Screen.sdl_screen.blit(text, (0, 0))
		pygame.display.flip()


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
