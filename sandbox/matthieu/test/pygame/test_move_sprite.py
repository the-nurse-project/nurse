#!/usr/bin/env python
import sys, os
import pygame

#-------------------------------------------------------------------------------
def update(dt):
	global x, state, width, delta
	delta2 = (delta * dt) * fps / 1000.
	if state == 0:
		x += delta2
		if x >= bg_width - perso_width: state = 1
	else:
		x -= delta2
		if x <= 0: state = 0


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
bg = pygame.image.load(os.path.join(path, 'hopital.png')).convert()
bg_width, bg_height = bg.get_width(), bg.get_height()
perso_width, perso_height = perso.get_width(), perso.get_height()


# parameters
x, y = bg_width / 2, bg_height / 2 - perso_height
fps = 60.
state = 0
delta = 2.
previous_time = pygame.time.get_ticks()
font = pygame.font.Font(None, 40)
clock = pygame.time.Clock()


# event loop
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
	time = pygame.time.get_ticks()
	dt = time - previous_time
	if dt < (1000. / fps): continue
	clock.tick()
	true_fps = clock.get_fps()
	previous_time = time
	update(dt)
	screen.fill((0, 0, 0))
	screen.blit(bg, (0, 0))
	screen.blit(perso, (x, y))
	text = font.render(str(true_fps), True, (255, 255, 255), (0, 0, 0))
	screen.blit(text, (0, bg_height))
	pygame.display.flip()
