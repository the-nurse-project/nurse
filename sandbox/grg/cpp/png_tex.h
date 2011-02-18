#ifndef PNG_TEX_H
#define PNG_TEX_H


#include <GL/glut.h>


typedef struct
{
  GLsizei width;
  GLsizei height;

  GLenum format;
  GLint internalFormat;
  GLuint id;

  GLubyte *texels;

} gl_texture_t;

GLuint loadPNGTexture (const char *filename);
gl_texture_t * ReadPNGFromFile (const char *filename);

#endif
