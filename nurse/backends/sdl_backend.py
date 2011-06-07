import sys
import pygame

from nurse.backends import EventLoop, KeyBoardDevice, GraphicEngine, ImageProxy


class SdlEventLoop(EventLoop):
	def __init__(self, fps = 60.):
		EventLoop.__init__(self, fps)

	def start(self):
		previous_time = pygame.time.get_ticks()

		while 1:
			self.read_events()
			time = pygame.time.get_ticks()
			dt = time - previous_time
			if dt < (1000. / self.fps): continue
			previous_time = time
			self.update(dt)

	def update(self, dt):
		universe.context_manager.display()
		universe.context_manager.update(dt)

	def read_events(self):
		if len(self._pending_events) != 0:
			e = self._pending_events.pop()
			e.start()
		Config.get_keyboard_device().read_events()


class SdlKeyBoardDevice(KeyBoardDevice):
	keysym_map = {}
	for i in range(ord('a'), ord('z') + 1):
		key = 'K_' + chr(i)
		keysym_map[pygame.constants.__getattribute__(key)] = \
			KeyBoardDevice.constants.__getattribute__(key)
	for i in range(10):
		key = 'K_' + str(i)
		keysym_map[pygame.constants.__getattribute__(key)] = \
			KeyBoardDevice.constants.__getattribute__(key)
	for key in ['K_UP', 'K_DOWN', 'K_LEFT', 'K_RIGHT', 'K_ESCAPE',
		'K_SPACE', 'KEYDOWN', 'KEYUP', 'K_RETURN']:
		keysym_map[pygame.constants.__getattribute__(key)] = \
			KeyBoardDevice.constants.__getattribute__(key)
	
	def __init__(self):
		KeyBoardDevice.__init__(self)

	def read_events(self):
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
				pygame.constants.KEYUP]: return
		else:
			type = self._get_key_from_symbol(event.type)
			key = self._get_key_from_symbol(event.key)
			self.emit((type, key))


class SdlImageProxy(ImageProxy):
	def __init__(self, raw_image):
		ImageProxy.__init__(self, raw_image)

	def get_size(self):
		return self._raw_image.get_size()

	def get_width(self):
		return self._raw_image.get_size()[0]

	def get_height(self):
		return self._raw_image.get_size()[1]


class SdlGraphicEngine(GraphicEngine):
	display_map = {}

	def __init__(self, resolution, flags):
		GraphicEngine.__init__(self)
		pygame.init()
		pygame.font.init()
		self._screen = pygame.display.set_mode(resolution, flags)
		self._clock = pygame.time.Clock()
		self._font = pygame.font.Font(None, 40)
		# for examples TODO: find a better way
		self._img_path = '../data/pix'

	def display_sprite(self, screen, sprite):
		res = GraphicEngine.display_sprite(self, screen, sprite)
		self._screen.blit(*res)

	def display_dialog(self, screen, dialog):
		# FIXME
		pass

	def display_text(self, screen, text):
		# FIXME
		pass

	def display_fps(self, screen, fps):
		self._clock.tick()
		true_fps = self._clock.get_fps()
		text = self._font.render(str(true_fps), True,
			fps.fg_color, fps.bg_color)
		self._screen.blit(text, fps.get_location())

	def flip(self):
		pygame.display.flip()

	def clean(self):
		self._screen.fill((0, 0, 0))

	def get_uniform_surface(self, shift=(0, 0), size=None,
				color=(0, 0, 0), alpha=128):
		if size is not None:
			flags = self._screen.get_flags()
			surface = pygame.Surface(size, flags)
		else:	surface = self._screen.convert()
		surface.fill(color)
		surface.set_alpha(alpha)
		return SdlImageProxy(surface)

	def load_image(self, filename):
		surface = pygame.image.load(os.path.join(self._img_path,
							filename))
		alpha_color = (0xff, 0, 0xff)
		flags = pygame.constants.SRCCOLORKEY | pygame.constants.RLEACCEL
		surface.set_colorkey(alpha_color, flags)
		return SdlImageProxy(surface)

	def load_text(self, text, font='Times New Roman',
				font_size=20, x=0, y=0):
		return None #FIXME

	def get_screen(self):
		return SdlImageProxy(self._screen)
	

SdlGraphicEngine.display_map.update({ \
	'sprite' : SdlGraphicEngine.display_sprite,
	'dialog' : SdlGraphicEngine.display_dialog,
	'text' : SdlGraphicEngine.display_text,
	'fps' : SdlGraphicEngine.display_fps})
