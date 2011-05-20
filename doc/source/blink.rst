
A Blinking Example
******************

.. code-block:: python 

        #!/usr/bin/env python
        # -*- coding: iso-8859-15 -*-

        from nurse.base import *
        from nurse.config import Config
        from nurse.sprite import *
        from nurse.context import Context, ContextManager
        from nurse.screen import *
        from nurse.state_machine import *

        class Incrementator(Object):
                def __init__(self):
                        Object.__init__(self, 'default_name')
                        self._is_text_visible = True

                def on_time_event(self, event):
                        if self._is_text_visible:
                                self.context.set_visible(self.text, False)
                        else:
                                self.context.set_visible(self.text, True)
                        self._is_text_visible = not self._is_text_visible

        class Timer(Object):
                def start(self):
                        import pyglet
                        pyglet.clock.schedule_interval ( self.tick, 1 )
                def tick(self,dt):
                        self.emit("time_event")
                        print 'hello', dt

        class Blinker(StateMachine):
                def __init__(self, name='state machine', context=None):
                        StateMachine.__init__(self, name, context)
                        states = [State('visible'), State('not_visible')]
                        for state in states: self.add_state(state)
                        self.set_initial_state(states[0])

                def update(self, dt):
                        print dt
        #-------------------------------------------------------------------------------
        def main():
                Config.backend = 'pyglet'
                Config.init()

                #FIXME : find another way to add the device
                context_manager = ContextManager()
                universe.context_manager = context_manager

                # manage context
                properties_all_active = { 'is_visible' : True, 'is_active' : True,
                                        '_is_receiving_events' : True} 
                properties_not_receiving = { 'is_visible' : True, 'is_active' : False,
                                        '_is_receiving_events' : False}

                context = Context("Context", ** properties_all_active)
                context_manager.add_state(context)
                context_manager.set_initial_state(context)
                context_manager.start()

                resolution = Config.resolution
                geometry = (0, 0, resolution[0], resolution[1])

                screen_fixed = VirtualScreenRealCoordinates('fixed screen', geometry)

                # dialog context
                context.add_screen(screen_fixed)
                text = Text('text', context, 4, 'bonjour')
                text.set_location([100,100])
                incrementator = Incrementator()
                incrementator.text = text
                incrementator.context = context
                timer = Timer('timer')
                timer.start()
                timer.connect('time_event', incrementator, 'on_time_event')
                context_aux = Context("ContextAux", **properties_not_receiving)
                context_manager.add_state(context_aux)
                blinker = Blinker('blinker', context_aux)
                # FPS
                event_loop = Config.get_event_loop()
                event_loop.start()

        if __name__ == "__main__" : main()
