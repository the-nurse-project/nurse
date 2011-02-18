#include "rule.h"


/**
 * @brief Constructeur de State
 * @param n le nom de l'état
 * @param opt la liste d'options possibles
 * @param v la valeur par défaut 
 * @return l'état
 */

State::State(string n, set<string> opt, string v){
  name = n;
  options = *new set<string>(opt);
  value = v;
}

State::State(const char *n, const char *opt, const char *v){
  name = n;
  options.insert(opt);
  value = v;
}


/**
 * @brief Constructeur de GivenState, de type Action  
 * 
 * @param n le nom de l'objet concerné
 * @param opt le nom de l'action 
 * @return l'état
 */

GivenState::GivenState(string n, string opt){
  object = n;
  state = opt;
  operation = Operation();
  operation.value = "[action]";
  operation.operation_type = ACTION;
}

/**
 * @brief Constructeur de GivenState, de type Etat  
 * 
 * @param n le nom de l'objet concerné
 * @param opt le nom de l'état concerné
 * @param v la valeur de l'état concerné
 * @return l'état
 */

GivenState::GivenState(string n, string opt, string v, unsigned int format){
  object = n;
  state = opt;
  operation = Operation(v, format);
}



/**
 * @brief Constructeur de Rule
 * 
 * A partir d'un vecteur de conditions et d'un vecteur d'implications, construit une Rule
 * @param c les conditions
 * @param i les implications
 * @return la règle
 */

Rule::Rule(vector<GivenState> c, vector<GivenState> i){
  for (unsigned int j=0;j<c.size();j++){
    conditions.insert(pair<const char*, GivenState>(c[j].object.data(), c[j])); 
  }
  for (unsigned int j=0;j<i.size();j++){
    implications.insert(pair<const char*, GivenState>(i[j].object.data(), i[j])); 
  }
}
