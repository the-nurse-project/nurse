#ifndef IMAGE_H
#define IMAGE_H

#include <GL/gl.h>
#include <vector>
#include <string>
#include "vector.h"
#include "assert.h"
#include "png_tex.h"


using namespace std;


/*!
   @struct Image2D
   @brief Image couleur
  */
template <class T> class Image2D{
  protected:
    vector<vector<T> > data;

  public :
  string file;
  unsigned int width;	
  unsigned int height;
  Image2D(void){}
  Image2D(unsigned int widt, unsigned int heigh, int dept=1){
    width = widt;
    height = heigh;
    data = vector<vector<T> >(height, vector<T>(width) );
  }
  Image2D(const Image2D<T> &im){
    file = im.file;
    width = im.width;
    height = im.height;
    data = *(new vector<vector<T> >(im.data));
  }
  void ReadImage(const char *nom);
  void ReadImagePNG(const char *nom);
  void BasculeImage(GLubyte *N);

  void InsertSprite(Image2D<T> &sprite, unsigned int x, unsigned int y){
    assert(sprite.width+x < width && sprite.height + y < height);
    unsigned int i,j,k;
    unsigned char rgb[4];
    for (i=0;i<sprite.width;i++){
      for (j=0;j<sprite.height;j++){
        for (k=0;k<4;k++)
          rgb[k] = sprite[j][i][k];
        if (!(rgb[0] == 0 && rgb[1] == 0 && rgb[2] == 0))
          for (k=0;k<data[0][0].size();k++) 
            data[j+y][i+x][k] = sprite.data[j][i][k];
      }
    }
  }
  
  void InsertSprite(Image2D<T> &sprite, unsigned int x, unsigned int y, unsigned int depth){
    assert(sprite.width+x < width && sprite.height + y < height);
    unsigned int i,j,k;
    unsigned char rgb[4];
    for (i=0;i<sprite.width;i++){
      for (j=0;j<sprite.height;j++){
        for (k=0;k<4;k++)
          rgb[k] = sprite[j][i][k];
        if (!(rgb[0] == 0 && rgb[1] == 0 && rgb[2] == 0))
          for (k=0;k<data[0][0].size();k++) 
            data[j+y][i+x][k] = sprite.data[j][i][k];
      }
    }
  }
  
  
  
  vector<T> &operator[](unsigned int i){
    return data[i];
  }
};


typedef Image2D<Vector<unsigned char,4> > Image2DColor;
typedef Image2D<int> Image2D1;
#endif

