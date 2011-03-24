from ..base import Object
from enum import Enum

class EventLoop(Object):
	def __init__(self, fps = 60.):
		Object.__init__(self, 'event_loop')
		self.fps = fps
		self._pending_events = []

	def add_event(self, event):
		self._pending_events.append(event)

	def get_events(self):
		try:
			yield self._pending_events.pop()
		except IndexError: pass


class KeyBoardDevice(Object):
	constants = Enum(*(['KEYDOWN', 'KEYUP'] + \
		['K_' + chr(i) for i in range(ord('a'), ord('z') + 1)] + \
		['K_' + str(i) for i in range(10)] + \
		['K_UP', 'K_DOWN', 'K_LEFT', 'K_RIGHT', 'K_ESCAPE', 'K_SPACE']+\
		['UNKNOWN']))

	def __init__(self):
		Object.__init__(self, 'keyboard_device')

	@classmethod
	def _get_key_from_symbol(cls, symbol):
		try:
			return cls.keysym_map[symbol]
		except:
			print "warning: symbol '%d' is not handle" % symbol
			return cls.constants.UNKNOWN


class ImageProxy(object):
	def __init__(self, raw_image):
		self._raw_image = raw_image

	def get_raw_image(self):
		return self._raw_image


class GraphicEngine(object):
	# GraphicEngine and derivated classes are singletons
	instances = {}

	def __new__(cls, *args, **kwargs):
		if GraphicEngine.instances.get(cls) is None:
			GraphicEngine.instances[cls] = object.__new__(cls)
		return GraphicEngine.instances[cls]

	def display_context(self, screen, context):
		data = context.get_visible_data()
		for layer, objects in data.items(): # from bg to fg
			for obj in objects:
				self.display_object(screen, obj)
	
	def display_object(self, screen, obj):
		# FIXME: move somewherelse
		from ..sprite import FpsSprite, Dialog, Text, Sprite 
		if isinstance(obj, FpsSprite):
			type = 'fps'
		elif isinstance(obj, Dialog):
			type = 'dialog'
		elif isinstance(obj, Text):
			type = 'text'
		elif isinstance(obj, Sprite):
			type = 'sprite'
		else:	type = None
		self.display_map[type](self, screen, obj)

	def display_sprite(self, screen, sprite):
		import pygame # FIXME : replace
		time = pygame.time.get_ticks()
		frame_proxy, center = sprite.get_frame_infos(time)
		if frame_proxy is None: return
		raw_img = frame_proxy.get_raw_image()
		dst_pos = screen.get_ref() + sprite.get_location() - center
		src_rect = None # FIXME : clip the area to blit
		return (raw_img, dst_pos, src_rect)

	def flip(self):
		raise NotImplementedError

	def clean(self):
		raise NotImplementedError

	def load_text(self, text, font='Times New Roman',
				font_size=20, x=0, y=0):
		raise NotImplementedError

	def load_image(self, filename):
		raise NotImplementedError

	def load_image(self, filename):	
		raise NotImplementedError

	def get_uniform_surface(self, shift=(0, 0), size=None,
				color=(0, 0, 0), alpha=128):
		raise NotImplementedError
