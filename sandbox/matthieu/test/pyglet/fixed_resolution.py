#!/usr/bin/env python
from pyglet.gl import *
import pyglet


class FixedResolutionViewport(object):
    def __init__(self, window, width, height, filtered=False):
        self.window = window
        self.width = width
        self.height = height
        self.texture = pyglet.image.Texture.create(width, height, 
            rectangle=True)

        if not filtered:
            # By default the texture will be bilinear filtered when scaled
            # up.  If requested, turn filtering off.  This makes the image
            # aliased, but is more suitable for pixel art.
            glTexParameteri(self.texture.target, 
                GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(self.texture.target, 
                GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    
    def begin(self):
        glViewport(0, 0, self.width, self.height)
        self.set_fixed_projection()

    def end(self):
        buffer = pyglet.image.get_buffer_manager().get_color_buffer()
        self.texture.blit_into(buffer, 0, 0, 0)

        glViewport(0, 0, self.window.width, self.window.height)
        self.set_window_projection()

        aspect_width = self.window.width / float(self.width)
        aspect_height = self.window.height / float(self.height)
        if aspect_width > aspect_height:
            scale_width = aspect_height * self.width
            scale_height = aspect_height * self.height
        else:
            scale_width = aspect_width * self.width
            scale_height = aspect_width * self.height
        x = (self.window.width - scale_width) / 2
        y = (self.window.height - scale_height) / 2
        
        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        glColor3f(1, 1, 1)
        self.texture.blit(x, y, width=scale_width, height=scale_height)
    
    def set_fixed_projection(self):
        # Override this method if you need to change the projection of the
        # fixed resolution viewport.
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        glMatrixMode(GL_MODELVIEW)

    def set_window_projection(self):
        # This is the same as the default window projection, reprinted here
        # for clarity.
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.window.width, 0, self.window.height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
