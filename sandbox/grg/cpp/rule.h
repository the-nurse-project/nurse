#ifndef RULE_H
#define RULE_H

#include <set>
#include <vector>
#include <string.h>
#include <map>
#include "operation.h"

using namespace std;


struct ltstr
{
  bool operator()(const char* s1, const char* s2) const
  {
    return strcmp(s1, s2) < 0;
  }
};

/**
* @brief Classe State
*
* La classe des états : un état est défini par un nom (ex. ouverture), un ensemble d'options (contrairement à un GivenState) et une valeur (sous forme de chaîne à ce jour).
*/

class State{
  public:
    string name;
    set<string> options;
    unsigned int type;
    string value;
    State(void){}    
    State(string n, set<string> opt, string v);
    State(const char *n, const char *opt, const char *v);
};

/**
* @brief Classe GivenState
*
* Un objet de la classe GivenState est un état (en cela comparable aux objets de classe State) mais dont la valeur est fixée ; il n'y a pas d'options possibles
*/

class GivenState{
  public:
    string object;
    string state;
    Operation operation;
    GivenState(){}
    GivenState(string n, string opt);
    GivenState(string n, string opt, string v, unsigned int format);

};

/**
* @brief Classe Rule
* 
* La classe qui stocke les conditions et implications de chaque règle.
* 
*/

class Rule{
  public:
    multimap<const char *, GivenState, ltstr> conditions;
    multimap<const char *, GivenState, ltstr> implications;
    Rule(void){}
    Rule(vector<GivenState> c, vector<GivenState> i);
};

#endif

