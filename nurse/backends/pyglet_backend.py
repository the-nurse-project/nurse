import sys
import pyglet
from pyglet.gl import *

from nurse.backends import EventLoop, KeyBoardDevice, GraphicEngine, ImageProxy
from nurse.base import universe

class PygletEventLoop(EventLoop):
	def __init__(self, fps = 60.):
		EventLoop.__init__(self, fps)

	def start(self):
		pyglet.clock.schedule_interval(self.update, 1. / self.fps)
		pyglet.app.run()

	def update(self, dt):
		'''
    dt : delay in seconds between 2 calls of this method
                '''
		self.read_events()
		universe.context_manager.update(dt * 1000.)

	@classmethod
	def on_draw(cls):
		universe.context_manager.display()

	def read_events(self):
		if len(self._pending_events) != 0:
			e = self._pending_events.pop()
			e.start()


class PygletKeyBoardDevice(KeyBoardDevice):
	fullscreen = False
	keysym_map = {}
	for i in range(ord('a'), ord('z') + 1):
		key = chr(i)
		keysym_map[pyglet.window.key.__getattribute__(key.upper())] = \
			KeyBoardDevice.constants.__getattribute__('K_' + key)
	for i in range(10):
		key = str(i)
		keysym_map[pyglet.window.key.__getattribute__('NUM_' + key)] = \
			KeyBoardDevice.constants.__getattribute__('K_' + key)
	for key in ['UP', 'DOWN', 'LEFT', 'RIGHT', 'ESCAPE', 'SPACE']:
		keysym_map[pyglet.window.key.__getattribute__(key)] = \
			KeyBoardDevice.constants.__getattribute__('K_' + key)

	def __init__(self):
		KeyBoardDevice.__init__(self)
		self._win = None

	def attach_window(self, win):
		self._win = win
		self.on_key_press = win.event(self.on_key_press)
		self.on_key_release = win.event(self.on_key_release)

	def on_key_press(self, symbol, modifiers):
		if symbol == pyglet.window.key.ESCAPE or \
			symbol == pyglet.window.key.Q:
			sys.exit()
		elif symbol == pyglet.window.key.F:
			self._win.set_fullscreen(self.fullscreen)
			self.fullscreen = not self.fullscreen
		
		key = self._get_key_from_symbol(symbol)
		self.emit((KeyBoardDevice.constants.KEYDOWN, key))
		return pyglet.event.EVENT_HANDLED

	def on_key_release(self, symbol, modifiers):
		key = self._get_key_from_symbol(symbol)
		self.emit((KeyBoardDevice.constants.KEYUP, key))
		return pyglet.event.EVENT_HANDLED


class PygletImageProxy(ImageProxy):
	def __init__(self, raw_image):
		ImageProxy.__init__(self, raw_image)

	def get_size(self):
		if self._raw_image is None: return 0, 0 #FIXME
		return self._raw_image.width, self._raw_image.height

	def get_width(self):
		return self._raw_image.width

	def get_height(self):
		return self._raw_image.height


class PygletUniformSurface(object):
	def __init__(self, shift, size, color, alpha):
		self._x, self._y = int(shift[0]), int(shift[1])
		self.width = int(size[0])
		self.height = int(size[1])
		x2, y2 = self.width, self.height
		self._batch = pyglet.graphics.Batch()
		self._batch.add(4, GL_QUADS, None,
			('v2i', [0, 0, x2, 0, x2, y2, 0, y2]),
			('c4B', (list(color) + [int(alpha)]) * 4))

	def set_position(self, x, y):
		self._x = x
		self._y = y

	def draw(self):
		glPushMatrix()
		glTranslatef(self._x, self._y, 0)
		glEnable(GL_BLEND)
		self._batch.draw()
		glDisable(GL_BLEND)
		glPopMatrix()


class PygletGraphicEngine(GraphicEngine):
	display_map = {}
	
	def __init__(self, resolution, caption):
		GraphicEngine.__init__(self)
		pyglet.resource.path.append('../data/pix')
		pyglet.resource.reindex()
		self._win = pyglet.window.Window(resolution[0], resolution[1],
							caption=caption)
		self._fps_display = pyglet.clock.ClockDisplay()

	def _invert_y_axis(self, img_height, pos_y):
		return self._win.height - pos_y - img_height

	def display_context(self, screen, context):
		# clipping according to screen geometry
		x, y, width, height = screen.geometry
		glViewport(x, y, width, height)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glOrtho(x, x + width, y, y + height, -1, 1)
		glMatrixMode(GL_MODELVIEW)

		GraphicEngine.display_context(self, screen, context)

	def display_sprite(self, screen, sprite):
		sprite, dst_pos, src_rect = GraphicEngine.display_sprite(self,
							screen, sprite)
		dst_pos[1] = self._invert_y_axis(sprite.height, dst_pos[1])
		sprite.set_position(*dst_pos)
		sprite.draw()

	def display_dialog(self, screen, dialog):
		repr_list = dialog._current_state.list_backend_repr
		for repr in repr_list: repr.draw()

	def display_text(self, screen, text):
		repr = text.backend_repr
		if repr is not None: repr.draw()

	def display_fps(self, screen, fps):
		pos = list(fps.get_location())
		pos[1] = self._invert_y_axis(self._fps_display.label.height,
								pos[1])
		self._fps_display.label.x = pos[0]
		self._fps_display.label.y = pos[1]
		self._fps_display.draw()

	def flip(self):
		pass # nothing to do

	def clean(self):
		self._win.clear()

	def get_uniform_surface(self, shift=(0, 0), size=None,
				color=(0, 0, 0), alpha=128):
		if size is None: size = self._win.width, self._win.height
		surface = PygletUniformSurface(shift, size, color, alpha)
		return PygletImageProxy(surface)

	def load_image(self, filename):
		img = pyglet.resource.image(filename)
		sprite = pyglet.sprite.Sprite(img, 0, 0)
		return PygletImageProxy(sprite)

	def load_text(self, text, font='Times New Roman',
				font_size=20, x=0, y=0):
		label = pyglet.text.Label(text, font_name=font,
				font_size=font_size, x=x, y=y)
		label.y = self._invert_y_axis(label.content_height, y)
		return label

	def shift_text(self, text, shift):
		repr_list = text.list_backend_repr
		for repr in repr_list: repr.y += shift
			
	def get_screen(self):
		return PygletImageProxy(self._win)
	

PygletGraphicEngine.display_map.update({ \
	'sprite' : PygletGraphicEngine.display_sprite,
	'dialog' : PygletGraphicEngine.display_dialog,
	'text' : PygletGraphicEngine.display_text,
	'fps' : PygletGraphicEngine.display_fps})
