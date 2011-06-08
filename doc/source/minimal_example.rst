.. Minimal example

A Minimal Example
******************

.. code-block:: python

        #!/usr/bin/env python
        # -*- coding: iso-8859-15 -*-

        from nurse.base import *
        from nurse.config import Config
        from nurse.context import Context, ContextManager
        from nurse.screen import *

        #-------------------------------------------------------------------------------
        def main():
                Config.backend = 'pyglet'
                Config.init()

                context_manager = ContextManager()
                universe.context_manager = context_manager

                properties_all_active = { 'is_visible' : True, 'is_active' : True,
                                        '_is_receiving_events' : True} 
                context = Context('context', ** properties_all_active)
                context_manager.add_state(context)
                context_manager.set_initial_state(context)
                context_manager.start()

                resolution = Config.resolution
                geometry = (0, 0, resolution[0], resolution[1])

                screen_fixed = VirtualScreenRealCoordinates('fixed screen', geometry)
                context.add_screen(screen_fixed)

                event_loop = Config.get_event_loop()
                event_loop.start()

        if __name__ == "__main__" : main()


