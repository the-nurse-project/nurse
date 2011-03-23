import numpy as np

from base import Object
from config import Config

class VirtualScreen(Object):
	def __init__(self, name, geometry=(0, 0, 320, 200)):
		self._x, self._y, self._width, self._height = geometry

	def display(self, obj):
		Config.get_graphic_engine().display(self, obj)

	def get_ref(self):
		'''
    Return the referential coordinates (top-left corner of the virtual screen
    defined in real screen pixel coordinates).
		'''
		return self._ref_center


class VirtualScreenWorldCoordinates(VirtualScreen):
	def __init__(self, name='default_screen', geometry=(0, 0, 320, 200),
				focus=np.array([0, 0]), focus_on=None):
		'''
    name:       name of the screen
    geometry:   geometry of the screen: tuple (x, y, w, h):
                x: x position of the bottom left border in screen coordinates
                y: y position of the bottom left border in screen coordinates
                w: width of the screen in pixels
                h: height of the screen in pixels
    focus:      position in world coordinates on which the screen is focused
                (center of the screen).
    focus_on:   follow location of the given object (call get_location() func).
		'''
		VirtualScreen.__init__(self, name, geometry)
		self.set_focus(focus)
		if focus_on is not None:
			focus_on.connect("location_changed", self,
				"on_focus_changed", asynchronous=False)
		self.dst_pos = None

	def set_focus(self, focus):
		self._ref_center = np.array([self._x + self._width / 2,
					self._y + self._height / 2]) - focus
		self._focus = focus

	def on_focus_changed(self, event):
		location = event.signal_data
		self.set_focus(location)


class VirtualScreenRealCoordinates(VirtualScreen):
	def __init__(self, name='default_screen_real_coords',
			geometry=(0, 0, 320, 200)):
		VirtualScreen.__init__(self, name, geometry)
		self._ref_center = np.array([self._x, self._y])
