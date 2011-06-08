
An Example Between Timer and Space
***********************************

.. code-block:: python

        #!/usr/bin/env python

        from nurse import *
        from nurse.base import *
        from nurse.config import *
        from nurse.sprite import *
        from nurse.context import *
        from nurse.backends import *
        from nurse.screen import *


        class Incrementator(Object):
                def __init__(self):
                        Object.__init__(self, 'default_name')
                        self.text_visible = True
                def on_space_press(self, event):
                        if self.text.text == 'plop':
                                self.text.text = 'plip'
                        else:
                                self.text.text = 'plop'
                def on_time_event(self, event):
                        if self.text.text == 'plup':
                                self.text.text = 'plap'
                        else:
                                self.text.text = 'plup'

        class Timer(Object):
                def start(self):
                        import pyglet
                        pyglet.clock.schedule_interval ( self.tick, 1 )
                def tick(self,dt):
                        self.emit("time_event")
                        print 'hello', dt
                        
        #-------------------------------------------------------------------------------
        def main():
                # init
                Config.backend = 'pyglet'
                Config.init()

                context_manager = ContextManager()
                universe.context_manager = context_manager

                context = Context("context")
                geometry = (0, 0, Config.resolution[0], Config.resolution[1])
                screen = VirtualScreenRealCoordinates('main screen', geometry)
                context.add_screen(screen)

                context_manager.add_state(context)
                context_manager.set_initial_state(context)
                context_manager.start()

                # dynamic text
                text = Text('text', context, 4, 'plop', 'Times New Roman', 40)
                text.set_location(np.array([Config.resolution[0] / 2,
                                                Config.resolution[1] / 2]))
                text.stop()
                #text.start()

                incrementator = Incrementator()
                incrementator.text = text
                incrementator.context = context
                signal = (KeyBoardDevice.constants.KEYDOWN,
                                KeyBoardDevice.constants.K_SPACE)
                context.connect(signal, incrementator, "on_space_press" )

                t =  Timer('test')
                t.connect("time_event", incrementator, "on_time_event" )
                t.start()

                # start
                event_loop = Config.get_event_loop()
                event_loop.start()

        if __name__ == "__main__" : main()
