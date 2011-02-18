
#ifndef BASE_H
#define BASE_H

#include "object.h"
#include "vector.h"
#include "operation.h"





/** 
* @brief Classe Universe
*
* La classe qui regroupe la liste des objets et des règles de la scène avec des fonctions de lecture/écriture de fichiers XML sur le disque, des fonctions de mise à jour de l'état de l'univers, des fonctions initialisant le buffer décrivant les profondeurs des objets représentés.
*/

class Universe{
  
  protected:
    string filename;
    bool isRempliesConditionsRegleWithActions( Rule &r, vector<GivenState> &actions );
    vector<unsigned int> satisfiedConditionsRulesWithActions( vector<GivenState> &actions );
    bool applyImplication( GivenState &implication );    
    
  public:
    vector< const char* > timers;
    map< const char *, Object, ltstr > objects;
    vector< Rule > rules;
    
    Universe( void ){}
    Universe( const char *filename, int mode = 0 );
    
    map< const char*, Object *, ltstr > getObjectsOfClass( const char *classe );
    void update( vector< GivenState > &actions, unsigned int verbose=0, unsigned int save = 0 );
    void saveToDisk( const char *filename );
    void loadTextures( map< const char*, unsigned int, ltstr > &images );
    void RegisterTimers( void );
    int computeOperation( Operation op );

};

#endif

