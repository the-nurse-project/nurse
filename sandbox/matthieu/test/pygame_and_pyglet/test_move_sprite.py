#!/usr/bin/env python
import threading, time
import sys, os
import pygame
import sys
import pyglet
from pyglet.gl import *

#-------------------------------------------------------------------------------
# pyglet data/info

pyglet.resource.path.append('../../challenges/challenge1/pix/')
pyglet.resource.reindex()
img = pyglet.resource.image('perso.png')
bg_pyglet = pyglet.resource.image('hopital.png')

resolution = bg_pyglet.width, bg_pyglet.height
x, y = resolution[0] / 2, resolution[1] / 2
sprite = pyglet.sprite.Sprite(img, x, y)
win = pyglet.window.Window(resolution[0], resolution[1], caption='test')


context = win.context
config = context.config


fps = 60.
state = 0
delta = 2.
fullscreen = False

fps_display = pyglet.clock.ClockDisplay()

#-------------------------------------------------------------------------------
# pygame data/info

# init
pygame.init()
pygame.font.init()
resolution = 800, 600
flags = pygame.constants.DOUBLEBUF | pygame.constants.HWSURFACE | \
					pygame.constants.HWACCEL
screen = pygame.display.set_mode(resolution, flags)

# load data
path = '../../challenges/challenge1/pix/'
perso = pygame.image.load(os.path.join(path, 'perso.png'))
bg_pygame = pygame.image.load(os.path.join(path, 'hopital.png')).convert()
bg_width, bg_height = bg_pygame.get_width(), bg_pygame.get_height()
perso_width, perso_height = perso.get_width(), perso.get_height()


# parameters
x, y = bg_width / 2, bg_height / 2 - perso_height
fps = 60.
state = 0
delta = 2.
font = pygame.font.Font(None, 40)
clock = pygame.time.Clock()


#-------------------------------------------------------------------------------
# events and updates

def update_pygame(dt):
	global x, state, width, delta
	delta2 = (delta * dt) * fps / 1000.
	if state == 0:
		x += delta2
		if x >= bg_width - perso_width: state = 1
	else:
		x -= delta2
		if x <= 0: state = 0


@win.event
def on_key_press(symbol, modifiers):
	global fullscreen
	if symbol == pyglet.window.key.ESCAPE or \
		symbol == pyglet.window.key.Q:
		sys.exit()
	elif symbol == pyglet.window.key.F:
		win.set_fullscreen(fullscreen)
		fullscreen = not fullscreen
	return pyglet.event.EVENT_HANDLED


@win.event
def on_draw():
	win.clear()
	bg_pyglet.blit(0, 0)
	sprite.draw()
	fps_display.draw()

def update_pyglet(dt):
	delta2 = (delta * dt) * fps
	global state
	if state == 0:
		sprite.x += delta2
		if sprite.x >= resolution[0] - img.width: state = 1
	else:
		sprite.x -= delta2
		if sprite.x <= 0: state = 0

class ThreadedPygame(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		previous_time = pygame.time.get_ticks()
		# pygame event loop
		while 1:
			# events
			event = pygame.event.poll()
			if (event.type == pygame.constants.QUIT): sys.exit(0)
			elif (event.type == pygame.constants.KEYDOWN):
				keymap = pygame.key.get_pressed()
				if keymap[pygame.constants.K_q] or \
					keymap[pygame.constants.K_ESCAPE]:
					sys.exit(0)
				elif keymap[pygame.constants.K_f]:
					pygame.display.toggle_fullscreen()

			# time
			cur_time = pygame.time.get_ticks()
			dt = cur_time - previous_time
			time.sleep(0.01)
			if dt < (1000. / fps): continue
			clock.tick()
			true_fps = clock.get_fps()
			previous_time = cur_time
			update_pygame(dt)
			screen.fill((0, 0, 0))
			screen.blit(bg_pygame, (0, 0))
			screen.blit(perso, (x, y))
			text = font.render(str(true_fps), True, (255, 255, 255), (0, 0, 0))
			screen.blit(text, (0, bg_height))
			pygame.display.flip()
#-------------------------------------------------------------------------------
# 

th_pygame = ThreadedPygame()
th_pygame.start()

pyglet.clock.schedule_interval(update_pyglet, 1. / fps)
pyglet.app.run()
