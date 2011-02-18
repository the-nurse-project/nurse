#define MAXLENGTH 20
#include "object.h"
#include <stdio.h>
#include <cstdlib>

/**
 * @brief Constructeur d'Object
 * 
 * A partir d'un nom, d'une classe, d'une géométrie, d'une liste d'états et d'une liste d'actions possibles, crée un objet.
 * @param n le nom de l'objet
 * @param C la classe
 * @param geom la géométrie (polygonale)
 * @param st la liste d'états
 * @param act la liste d'actions possible
 * @return l'objet
 */

Object::Object(string n, string C, map<const char*, Vector<Point3di,4>, ltstr> &geom, map<const char *, State, ltstr> st, set<string> &act){
  name = n;
  Class = C;
  geometries = *(new map<const char*, Vector<Point3di,4>, ltstr>(geom));
  states = *(new map<const char *, State, ltstr>(st));
  actions = *new set<string>(act);
}

/**
 * @brief Renvoit la position définie dans 3 états nommés POSITION_ABSCISSA ORDINATE et DEPTH
 * 
 * Il faudra comme ailleurs songer à remplacer tout ça par des variables génériques.
 */

bool Object::getPosition(Point3di &p){
  map<const char *, State, ltstr>::iterator iter;
  int x=-1,y=-1,z=-1;
  iter = states.find("POSITION_ABSCISSA");
  if (iter != states.end()){
    x = atoi((*iter).second.value.data());
  }
  else return false;
  iter = states.find("POSITION_ORDINATE");
  if (iter != states.end()){
    y = atoi((*iter).second.value.data());
  }
  else return false;
  iter = states.find("POSITION_DEPTH");
  if (iter != states.end()){
    z = atoi((*iter).second.value.data());
  }
  else return false;
  p[0]=x; p[1]=y; p[2]=z;
  return true;
}


/**
 * @brief Convertit un objet en chaîne de caractères de sorte à pouvoir l'afficher
 *
 */

const char *Object::toString(void){
  char buffer[5];
  string s = "objet \"";
  s += name; s += "\" de classe ";
  s += Class; 
  Point3di position;
  if (getPosition(position)){
    s += "\n  Position x=";
    sprintf(buffer, "%d", position[0]);
    s += buffer;
    s += " ; y=";
    sprintf(buffer, "%d", position[1]);
    s += buffer;
    s += " ; z=";
    sprintf(buffer, "%d", position[2]);
    s += buffer;
    s += "\n";
  }
  set<string>::iterator it;
  map<const char *, State, ltstr>::iterator ite;
  for (ite=states.begin();ite!=states.end();ite++){
    if (strcmp((*ite).first, "POSITION_ABSCISSA")!=0 && strcmp((*ite).first, "POSITION_ORDINATE")!=0 && strcmp((*ite).first, "POSITION_DEPTH")!=0){
      s += "  etat \"";
      s += (*ite).second.name;
      s += "\" : ";
      for (it = (*ite).second.options.begin(); it !=(*ite).second.options.end();it++){
        s += *it;
        s += " / ";
      }
      s = s.substr(0,s.length()-2);
      s += " - ";
      s += (*ite).second.value;
      s += "\n";
    }
  }
  for (it = actions.begin(); it !=actions.end();it++){
    s += " ";
    s += *it;
    s += " - ";
  }
  if (actions.size() != 0)
    s = s.substr(0,s.length()-2);
  return s.data();
}

