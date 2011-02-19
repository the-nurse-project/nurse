#!/usr/bin/env python
import sys
import pyglet
import pyglet.window.key
import cocos

from cocos.director import director
from cocos.scene import Scene
from cocos.layer import Layer
from cocos.sprite import Sprite



class PersoLayer(Layer):
	is_event_handler = True

	def __init__(self, bg):
		super(PersoLayer, self).__init__()
		sprite = Sprite('perso.png')
		x = bg.position[0] + bg.image.width / 2
		y = bg.position[1] + bg.image.height / 2
		sprite.position = x, y
		actionL = cocos.actions.MoveBy((-bg.image.width / 2, 0), 2.)
		actionR = cocos.actions.Reverse(actionL)
		sprite.do(cocos.actions.Repeat(actionL + actionR + \
						actionR + actionL))
		self.add(sprite)

	def on_key_press(self, keys, mod):
		if keys == pyglet.window.key.ESCAPE or \
			keys == pyglet.window.key.Q:
			sys.exit()
		elif keys == pyglet.window.key.F:
			director.window.set_fullscreen(\
				not director.window.fullscreen)
		return True


class BgLayer(Layer):
	def __init__(self):
		super(BgLayer, self).__init__()
		self.image = pyglet.resource.image('hopital.png')

	def draw(self):
		self.image.blit(0, 0)


def main():
	# data
	pyglet.resource.path.append('../../challenges/challenge1/pix/')
	pyglet.resource.reindex()
	resolution = 800, 600

	# init
	director.init(width=resolution[0], height=resolution[1])

	# scene
	bg = BgLayer()
	perso = PersoLayer(bg)

	scene = Scene()
	scene.position = (resolution[0] - bg.image.width) / 2, \
			(resolution[1] - bg.image.height) / 2, 
	scene.add(bg)
	scene.add(perso)

	# run
	director.set_show_FPS(True)
	director.run(scene)


if __name__ == "__main__": main()

