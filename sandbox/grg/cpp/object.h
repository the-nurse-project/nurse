
#ifndef OBJECT_H
#define OBJECT_H

#include "image.h"
#include "rule.h"
#include "vector.h"




using namespace std;

/**
* @brief Class Object
* 
* La classe qui stocke les informations relatives à chaque objet : nom, classe (type générique), géométrie, états, actions possibles.
*/

class Object{
  public:
    string name;
    string Class;
    map<const char*,Vector<Point3di,4>,ltstr> geometries;
    map<const char *, State, ltstr> states;
    set<string> actions;
    Object(void){}
    Object(string n, string C, map<const char*, Vector<Point3di,4>, ltstr> &geom, map<const char *, State, ltstr> st, set<string> &act);
    bool getPosition(Point3di &p);
    const char *toString(void);
    void setImage(const char *, const char *);
    int get2DDepth(void);
};

#endif
