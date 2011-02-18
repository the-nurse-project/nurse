/*
 * png.c -- png texture loader
 * last modification: feb. 5, 2006
 *
 * Copyright (c) 2005-2006 David HENRY
 *
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated documentation
 * files (the "Software"), to deal in the Software without
 * restriction, including without limitation the rights to use,
 * copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT.
 * IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
 * ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
 * CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 * WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 * gcc -Wall -ansi -L/usr/X11R6/lib -lGL -lGLU -lglut
 *    `libpng12-config --cflags --libs` png.c -o png
 */
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <png.h>
#include "png_tex.h"






/* OpenGL texture info */



/* texture Id */
GLuint texId;


void
GetPNGtextureInfo (int color_type, gl_texture_t *texinfo)
{
  switch (color_type)
    {
    case PNG_COLOR_TYPE_GRAY:
      texinfo->format = GL_LUMINANCE;
      texinfo->internalFormat = 1;
      break;

    case PNG_COLOR_TYPE_GRAY_ALPHA:
      texinfo->format = GL_LUMINANCE_ALPHA;
      texinfo->internalFormat = 2;
      break;

    case PNG_COLOR_TYPE_RGB:
      texinfo->format = GL_RGB;
      texinfo->internalFormat = 3;
      break;

    case PNG_COLOR_TYPE_RGB_ALPHA:
      texinfo->format = GL_RGBA;
      texinfo->internalFormat = 4;
      break;

    default:
      /* Badness */
      break;
    }
}


gl_texture_t *
ReadPNGFromFile (const char *filename)
{
  gl_texture_t *texinfo;
  png_byte magic[8];
  png_structp png_ptr;
  png_infop info_ptr;
  int bit_depth, color_type;
  FILE *fp = NULL;
  png_bytep *row_pointers = NULL;
  int i;

  /* open image file */
  fp = fopen (filename, "rb");
  if (!fp)
    {
      fprintf (stderr, "error: couldn't open \"%s\"!\n", filename);
      return NULL;
    }

  /* read magic number */
  fread (magic, 1, sizeof (magic), fp);

  /* check for valid magic number */
  if (!png_check_sig (magic, sizeof (magic)))
    {
      fprintf (stderr, "error: \"%s\" is not a valid PNG image!\n",
	       filename);
      fclose (fp);
      return NULL;
    }

  /* create a png read struct */
  png_ptr = png_create_read_struct
    (PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
  if (!png_ptr)
    {
      fclose (fp);
      return NULL;
    }

  /* create a png info struct */
  info_ptr = png_create_info_struct (png_ptr);
  if (!info_ptr)
    {
      fclose (fp);
      png_destroy_read_struct (&png_ptr, NULL, NULL);
      return NULL;
    }

  /* create our OpenGL texture object */
  texinfo = (gl_texture_t *)malloc (sizeof (gl_texture_t));

  /* initialize the setjmp for returning properly after a libpng
     error occured */
  if (setjmp (png_jmpbuf (png_ptr)))
    {
      fclose (fp);
      png_destroy_read_struct (&png_ptr, &info_ptr, NULL);

      if (row_pointers)
	free (row_pointers);

      if (texinfo)
	{
	  if (texinfo->texels)
	    free (texinfo->texels);

	  free (texinfo);
	}

      return NULL;
    }

  /* setup libpng for using standard C fread() function
     with our FILE pointer */
  png_init_io (png_ptr, fp);

  /* tell libpng that we have already read the magic number */
  png_set_sig_bytes (png_ptr, sizeof (magic));

  /* read png info */
  png_read_info (png_ptr, info_ptr);

  /* get some usefull information from header */
  bit_depth = png_get_bit_depth (png_ptr, info_ptr);
  color_type = png_get_color_type (png_ptr, info_ptr);

  /* convert index color images to RGB images */
  if (color_type == PNG_COLOR_TYPE_PALETTE)
    png_set_palette_to_rgb (png_ptr);

  /* convert 1-2-4 bits grayscale images to 8 bits
     grayscale. */
  if (color_type == PNG_COLOR_TYPE_GRAY && bit_depth < 8)
    png_set_gray_1_2_4_to_8 (png_ptr);

  if (png_get_valid (png_ptr, info_ptr, PNG_INFO_tRNS))
    png_set_tRNS_to_alpha (png_ptr);

  if (bit_depth == 16)
    png_set_strip_16 (png_ptr);
  else if (bit_depth < 8)
    png_set_packing (png_ptr);

  /* update info structure to apply transformations */
  png_read_update_info (png_ptr, info_ptr);

  /* retrieve updated information */
  png_get_IHDR (png_ptr, info_ptr,
		(png_uint_32*)(&texinfo->width),
		(png_uint_32*)(&texinfo->height),
		&bit_depth, &color_type,
		NULL, NULL, NULL);

  /* get image format and components per pixel */
  GetPNGtextureInfo (color_type, texinfo);

  /* we can now allocate memory for storing pixel data */
  texinfo->texels = (GLubyte *)malloc (sizeof (GLubyte) * texinfo->width
	       * texinfo->height * texinfo->internalFormat);

  /* setup a pointer array.  Each one points at the begening of a row. */
  row_pointers = (png_bytep *)malloc (sizeof (png_bytep) * texinfo->height);

  for (i = 0; i < texinfo->height; ++i)
    {
      row_pointers[i] = (png_bytep)(texinfo->texels +
	((texinfo->height - (i + 1)) * texinfo->width * texinfo->internalFormat));
    }
  std::cout << texinfo->internalFormat << ";" << texinfo->id << ";" << texinfo->format << std::endl;
  /* read pixel data using row pointers */
  png_read_image (png_ptr, row_pointers);

  /* finish decompression and release memory */
  png_read_end (png_ptr, NULL);
  png_destroy_read_struct (&png_ptr, &info_ptr, NULL);

  /* we don't need row pointers anymore */
  free (row_pointers);

  fclose (fp);
  return texinfo;
}





GLuint
loadPNGTexture (const char *filename)
{
  gl_texture_t *png_tex = NULL;
  GLuint tex_id = 0;

  png_tex = ReadPNGFromFile (filename);

  if (png_tex && png_tex->texels)
    {
      /* generate texture */
      glGenTextures (1, &png_tex->id);
      glBindTexture (GL_TEXTURE_2D, png_tex->id);

      /* setup some parameters for texture filters and mipmapping */
      glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR/*_MIPMAP_LINEAR*/);
      glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);


      glTexImage2D (GL_TEXTURE_2D, 0, png_tex->internalFormat,
		    png_tex->width, png_tex->height, 0, png_tex->format,
		    GL_UNSIGNED_BYTE, png_tex->texels);

      /*
      gluBuild2DMipmaps (GL_TEXTURE_2D, png_tex->internalFormat,
			 png_tex->width, png_tex->height,
			 png_tex->format, GL_UNSIGNED_BYTE, png_tex->texels);
      */

      tex_id = png_tex->id;

      /* OpenGL has its own copy of texture data */
      free (png_tex->texels);
      free (png_tex);
    }

  return tex_id;
}


// void
// init (const char *filename)
// {
//   /* init OpenGL */
//   glClearColor (0.5f, 0.5f, 0.5f, 1.0f);
//   glShadeModel (GL_SMOOTH);
// 
//   glEnable (GL_DEPTH_TEST);
// 
//   glEnable (GL_BLEND);
//   glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
// 
//   /* load png texture */
//   if ( !(texId = loadPNGTexture (filename)))
//     {
//       fprintf (stderr, "failed to load %s! aborting\n", filename);
//       exit (-1);
//     }
// }
// 
// 
// void
// shutdownApp (void)
// {
//   glDeleteTextures (1, &texId);
// }
// 
// 
// void
// reshape (int w, int h)
// {
//   if (h == 0)
//     h = 1;
// 
//   glViewport (0, 0, (GLsizei)w, (GLsizei)h);
// 
//   glMatrixMode (GL_PROJECTION);
//   glLoadIdentity ();
//   gluPerspective (45.0, (GLfloat)w/(GLfloat)h, 0.1, 1000.0);
// 
//   glMatrixMode (GL_MODELVIEW);
//   glLoadIdentity ();
// 
//   glutPostRedisplay ();
// }
// 
// 
// void
// display (void)
// {
//   glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
//   glLoadIdentity ();
// 
//   glEnable (GL_TEXTURE_2D);
//   glBindTexture (GL_TEXTURE_2D, texId);
// 
//   /* draw quad */
//   glTranslatef (0.0, 0.0, -5.0);
//   glBegin (GL_QUADS);
//     glTexCoord2f (0.0f, 0.0f);
//     glVertex3f (-1.0f, -1.0f, 0.0f);
// 
//     glTexCoord2f (1.0f, 0.0f);
//     glVertex3f (1.0f, -1.0f, 0.0f);
// 
//     glTexCoord2f (1.0f, 1.0f);
//     glVertex3f (1.0f, 1.0f, 0.0f);
// 
//     glTexCoord2f (0.0f, 1.0f);
//     glVertex3f (-1.0f, 1.0f, 0.0f);
//   glEnd  ();
// 
//   glDisable (GL_TEXTURE_2D);
// 
//   glutSwapBuffers ();
// }
// 
// 
// void
// keyboard (unsigned char key, int x, int y)
// {
//   switch (key)
//     {
//     case 27: /* escape */
//       exit(0);
//       break;
//     }
// }
// 

// int
// main (int argc, char *argv[])
// {
//   if (argc < 2)
//     {
//       fprintf (stderr, "usage: %s filename.png\n", argv[0]);
//       return -1;
//     }
// 
//   glutInit (&argc, argv);
//   glutInitDisplayMode (GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH);
//   glutInitWindowSize (640, 480);
//   glutCreateWindow ("PNG Texture Demo");
// 
//   atexit (shutdownApp);
//   init (argv[1]);
// 
//   glutReshapeFunc (reshape);
//   glutDisplayFunc (display);
//   glutKeyboardFunc (keyboard);
// 
//   glutMainLoop ();
// 
//   return 0;
// }
