import sys
import pyglet
import pyglet.gl



# data
pyglet.resource.path.append('../../challenges/challenge1/pix/')
pyglet.resource.reindex()
img = pyglet.resource.image('perso.png')
bg = pyglet.resource.image('hopital.png')

resolution = bg.width, bg.height
x, y = resolution[0] / 2, resolution[1] / 2
sprite = pyglet.sprite.Sprite(img, x, y)
win = pyglet.window.Window(resolution[0], resolution[1], caption='Astraea')


context = win.context
config = context.config


state = 0
delta = 3
fullscreen = False


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


fps_display = pyglet.clock.ClockDisplay()


@win.event
def on_draw():
	bg.blit(0, 0)
	sprite.draw()
	fps_display.draw()


def update(dt):
	global state
	if state == 0:
		sprite.x += delta
		if sprite.x >= resolution[0] - img.width: state = 1
	else:
		sprite.x -= delta
		if sprite.x <= 0: state = 0

	
pyglet.clock.schedule_interval(update, 1/60.)
pyglet.app.run()
