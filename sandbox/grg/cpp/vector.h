
#ifndef VECTOR_H
#define VECTOR_H

#include <vector> 

using namespace std;


/**
* @brief Classe Point2di
* 
* Une classe ordinaire pour décrire des points 2D à coordonnées entières
*/
/**
* @brief Classe Point3df
* 
* Une classe ordinaire pour décrire des points 3D à coordonnées flottantes
*/

/**
* @brief Classe Point3di
* 
* Une classe ordinaire pour décrire des points 3D à coordonnées entières
*/


template <class T, int dim> class Vector{
  protected :
    vector<T> _value;
  public:
    
    Vector(void){
      _value = vector<T>(dim);
    }
    T &operator[](unsigned int i){
      return _value[i];
    }
    inline Vector(const T &x, const T &y){
      _value = vector<T>(dim);
      _value[0] = x;
      _value[1] = y;
    }
    inline Vector(vector<T> v){
      _value = vector<T>(dim);
      for (unsigned int i=0;i<dim;i++)
         _value[i] = v[i];
    }
};

typedef Vector<int, 2> Point2di;
typedef Vector<float, 2> Point2df;
typedef Vector<int, 3> Point3di;
typedef Vector<float, 3> Point3df;

#endif

