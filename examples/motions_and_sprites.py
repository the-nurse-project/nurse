#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from nurse.base import *
from nurse.config import Config
from nurse.sprite import *
from nurse.context import Context, ContextManager
from nurse.screen import *
from nurse.game.dialog import *

# FIXME: - dialog does not work yet (re-test with last devel from greg
#          dialog branch)
#        - add center_location parameter to all sprites 

def create_sprites(context):
	# sprites
	nurse = AnimatedSprite("nurse", context, layer=2)
	nurse.load_frames_from_filenames('__default__', ['infirmiere.png'],
							'centered_bottom', 1)
	nurse.start()

	text = Text('text', context, 2, 'I am a moving text',
					'Times New Roman', 40)
	text.start()

	uniform = UniformLayer('red', context, layer=2, size=(40, 40),
				color=(255, 0, 0), alpha=255)
	uniform.start()


	dialog = Dialog('dialog', context, layer=4)
	msg = [('player', 'first sentence', True),
		('player', 'second sentence', True),
		('player', 'third sentence', True)]
	states = []
	for i, (perso, txt, writing_machine_mode) in enumerate(msg):
		state = DialogState('state_%d' % i, txt, 'Times New Roman', 40,
			((0, 0), (400, 200)), perso, 20., writing_machine_mode)
		dialog.add_state(state)
		states.append(state)
	signal = (KeyBoardDevice.constants.KEYDOWN,
			KeyBoardDevice.constants.K_SPACE)
	for i in range(len(states) - 1):
		states[i].add_transition(context, signal, states[i + 1])
	dialog.set_initial_state(states[0])
	dialog.start()

	sprites = [nurse, text, uniform, dialog]

	# add motions to sprites
	checkpoint_n = len(sprites)
	std_path = np.vstack((np.linspace(0, 800, checkpoint_n),
			[0] * checkpoint_n)).T
	shift = 50 + sprites[0]._size[1]
	delta = (600 - shift) / checkpoint_n
	for i in range(checkpoint_n):
		path = std_path.copy()
		path[:, 1] = shift + i * delta
		motion = PathMotion(speed=250.)
		motion.set_path(path)
		sprites[i].set_motion(motion)
		motion.init(sprites[i], checkpoint=i)


#-------------------------------------------------------------------------------
def main():
	# config
	Config.backend = 'pyglet'
	Config.init()

	# init
	context_manager = ContextManager()
	universe.context_manager = context_manager
	resolution = Config.resolution
	context = Context("context")

	# context
	create_sprites(context)
	geometry = (0, 0, resolution[0], resolution[1])
	screen = VirtualScreenRealCoordinates('screen', geometry)
	context.add_screen(screen)
	context_manager.add_state(context)
	context_manager.set_initial_state(context)
	context_manager.start()

	# instruction text
	# FIXME : had a shift to center text
	shift_x = 200
	instr = Text('text', context, 4,
		'hit SPACE bar to get ahead in the dialog',
		'Times New Roman', 20)
	instr.set_location(np.array([Config.resolution[0] / 2 - shift_x,
		(Config.resolution[1] * 15) / 16]))

	# start
	event_loop = Config.get_event_loop()
	event_loop.start()

if __name__ == "__main__" : main()
