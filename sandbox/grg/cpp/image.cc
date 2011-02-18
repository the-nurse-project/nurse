#define MAXLIGNE 256  
#include "image.h"
#include <stdio.h>
#include <assert.h>


/*!
	@brief Allocation et creation du parametre \a Image en fonction du fichier \a nom
	@param nom Le nom du fichier \a Image
	@param Image L'image
	@return -1 si l'allocation a echoue
*/

template <> void Image2DColor::ReadImage(const char *nom)
{

  FILE *f;
  char s[MAXLIGNE];
  int widt, heigh, maxcolor, n, k;
  unsigned char ligne[2048];
  
  /* Ouverture du fichier */
  f = fopen (nom, "rb");
  if (f == NULL)
    {
      printf ("ERREUR fopen(%s)\n", nom);
      return;
    }
  
  /* Lecture MagicValue
   * On evite fscanf pour eviter buffer overflow */
  fgets (s, MAXLIGNE, f);
  if (s[0] != 'P' || s[1] != '6')
    {
      printf ("ERREUR MagicValue <> P6\n");
      fclose (f);
      return;
    }
  
  /* Lecture width height
   * On saute les ligne commencant par un '#' */
  do fgets (s, MAXLIGNE, f);
  while (s[0] == '#');
  sscanf (s, "%d %d", &widt, &heigh);
 
  /* Lecture maxgrey
   * On ne tient pas compte de maxcolors, qui est presque toujours 255.
   * On saute les ligne commenant par un '#' */
  do fgets (s, MAXLIGNE, f);
  while (s[0] == '#');
  sscanf (s, "%d", &maxcolor);
  
  width = widt;
  printf("width : %d \n", width);
  height = heigh;
  printf("height : %d \n", height);
//   data = *(new vector<vector<Vector<unsigned char, 4> > >(height));
  data = vector<vector<Vector<unsigned char,4> > >(height, vector<Vector<unsigned char,4> >(width) );
  
  for (n=0;n<height;n++){
      if (fread(ligne,sizeof(unsigned char)*width*3,1,f)!=1)
          return; /* Erreur de lecture */
      
      for (k=0;k<width*3;k++){
          data[n][k/3][k%3] = (unsigned char) ligne[k];
          if ((k+1)%3==0) {
            data[n][k/3][3] = (unsigned char) 0;
            
          }
      }
      
  }

  
  fclose (f);
  file = nom;
  return;
}

template <> void Image2DColor::ReadImagePNG(const char *nom)
{
  gl_texture_t *fil;
  fil = ReadPNGFromFile (nom);
  width = fil->width;
  printf("width : %d \n", width);
  height = fil->height;
  printf("height : %d \n", height);
  data = vector<vector<Vector<unsigned char,4> > >(height, vector<Vector<unsigned char,4> >(width) );
  printf("internalFormat : %d \n", fil->internalFormat);

  unsigned int n=0;
  
  for (unsigned int j=0;j<height;j++)
    for (unsigned int i=0;i<width;i++){
      for (unsigned int k=0;k<fil->internalFormat;k++){
        data[height-1-j][i][k] = fil->texels[n++];
      }
      for (unsigned int k=fil->internalFormat;k<4;k++)
        data[height-1-j][i][k] = 0;
    }

  file = nom;
  
  return;
}


/*!
	@brief Copie l' \a Image dans un bitmap OpenGL en inversant les lignes (i.e La premiere ligne devient la derniere, la seconde devient l'avant derniere ... etc ...
	Attention, le bitmap OpenGL doit etre alloue !
	@param Image L'image
	@param N Le bitmap OpenGL
	@return -1 si l'allocation a echoue
*/

template <> void Image2DColor::BasculeImage(GLubyte *N){ 
  int i, j,k,n=0; 
  for(i=0;i<height;i++) 
    for(j=0;j<width;j++) 
      for(k=0;k<4;k++)
        N[n++]=(GLubyte)data[height-1-i][j][k];

} 





	
