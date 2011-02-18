#define MAXLENGTH 20
#include "universe.h"
#include <stdio.h>
#include <libxml/xmlreader.h>
#include <assert.h>
#include <GL/glut.h>
#include "timer.h"



const char *OBJECT_TAG = "objet";
const char *OBJECT_CLASS_ATTR = "classe";
const char *STATE_TAG = "etat";
const char *IMAGE_TAG = "image";
const char *IMAGE_DEPTH_ATTR = "depth";
const char *POSITION_TAG = "position";
const char *GEOMETRY_TAG = "geometrie";
const char *OPTION_TAG = "option";
const char *ACTION_TAG = "action";
const char *STATE_NAME_ATTR = "name";
const char *VALUE_TAG = "valeur";
const char *POINT_ABSCISSA_ATTR = "abscisse";
const char *POINT_ORDINATE_ATTR = "ordonnée";
const char *POINT_DEPTH_ATTR = "profondeur";
const char *POINT_TAG = "point";
const char *NAME_TAG = "name";
const char *RULE_TAG = "regle";
const char *CONDITION_TAG = "condition";
const char *IMPLICATION_TAG = "implication";
const char *TYPE_ATTR = "type";

const char *INTEGER_ATTR = "INTEGER";
const char *FLOAT_ATTR = "FLOAT";
const char *STRING_ATTR = "STRING";
const char *BOOLEAN_ATTR = "BOOLEAN";

/**
 * @brief Sauvegarde un univers dans un fichier XML
 *
 * Il faudrait remplacer les balises écrites en dur par des variables du style OBJECT_TAG pour plus de généricité.
 * @param file le fichier de sauvegarde
 */

void Universe::saveToDisk(const char *file){
  string s = "<?xml version=\"1.0\"?>\n\n";
  s += "<univers>\n\n";
  set<string>::iterator it;
  map<const char *, Object, ltstr>::iterator ite;
  map<const char *, State, ltstr>::iterator iter;
  map<const char *, Vector<Point3di,4>, ltstr>::iterator Ite1;
  multimap<const char *, GivenState, ltstr>::iterator ite1;
  char buffer[5];
  for (ite=objects.begin();ite!=objects.end();ite++){
    s += "  <objet classe=\"";
    s += (*ite).second.Class;
    s += "\">\n    <name>";
    s += (*ite).second.name;
    s += "</name>\n";
    Point3di position;
    if ((*ite).second.getPosition(position)){
      s += "    <position abscisse=\"";
      sprintf(buffer, "%d", position[0]);
      s += buffer; 
      s += "\" ordonnée=\"";
      sprintf(buffer, "%d", position[1]);
      s += buffer;
      s += "\" profondeur=\"";
      sprintf(buffer, "%d", position[2]);
      s += buffer;
      s += "\"/>\n";
    }
    for (Ite1=(*ite).second.geometries.begin();Ite1!=(*ite).second.geometries.end();Ite1++){
      s += "    <geometrie name=\"";
      s += (*Ite1).first;
      s += "\">\n";
      for (uint j=0;j<4;j++){
        s += "      <point abscisse=\"";
        sprintf(buffer, "%d", (*Ite1).second[j][0]);
        s += buffer;
        s += "\" ordonnée=\"";
        sprintf(buffer, "%d", (*Ite1).second[j][1]);
        s += buffer;
        s += "\" profondeur=\"";
        sprintf(buffer, "%d", (*Ite1).second[j][2]);
        s += buffer;
        s += "\"/>\n";
      }
      s += "    </geometrie>\n";
    }

    for (iter=(*ite).second.states.begin();iter!=(*ite).second.states.end();iter++){
      if (strcmp((*iter).first, "POSITION_ABSCISSA")!=0 && strcmp((*iter).first, "POSITION_ORDINATE")!=0 && strcmp((*iter).first, "POSITION_DEPTH")!=0){
        s += "    <etat name=\"";
        s += (*iter).second.name;
        s += "\">\n";
        for (it = (*iter).second.options.begin(); it !=(*iter).second.options.end();it++){
          s += "      <option>";
          s += *it;
          s += "</option>\n";
        }
        s += "      <valeur type=\"";
        if ((*iter).second.type == STRING) s += STRING_ATTR;
        else if ((*iter).second.type == INTEGER) s += INTEGER_ATTR;
        else if ((*iter).second.type == FLOAT) s += FLOAT_ATTR;
        else if ((*iter).second.type == BOOLEAN) s += BOOLEAN_ATTR;
        s += "\">";
        s += (*iter).second.value;
        s += "</valeur>\n    </etat>\n"; 
      }
    }
    for (it = (*ite).second.actions.begin(); it !=(*ite).second.actions.end();it++){
      s += "    <action>";
      s += *it;
      s += "</action>\n";
    }
    s += "  </objet>\n\n";
  }
  for (uint i=0;i<rules.size();i++){
    s += "  <regle>\n";
    for (ite1=rules[i].conditions.begin(); ite1!=rules[i].conditions.end();ite1++){
      s += "    <condition>\n      <objet>";
      s += (*ite1).second.object;
      s += "</objet>\n";
      if ((*ite1).second.operation.operation_type == ACTION){
        s += "      <action>";
        s += (*ite1).second.state;
        s += "</action>\n";
      }
      else {
        s += "      <etat>";
        s += (*ite1).second.state;
        s += "</etat>\n      <valeur";
        if ((*ite1).second.operation.operation_type == OPERATION) s+= " type=\"FUNCTION\"";
        s += ">";
        s += (*ite1).second.operation.toString();
        s += "</valeur>\n"; 
      }
      s += "    </condition>\n";
    }
    for (ite1=rules[i].implications.begin();ite1!=rules[i].implications.end();ite1++){
      s += "    <implication>\n      <objet>";
      s += (*ite1).second.object;
      s += "</objet>\n";
      if ((*ite1).second.operation.operation_type == ACTION){
        s += "      <action>";
        s += (*ite1).second.state;
        s += "</action>\n";
      }
      else {
        s += "      <etat>";
        s += (*ite1).second.state;
        s += "</etat>\n      <valeur";
        if ((*ite1).second.operation.operation_type == OPERATION) s+= " type=\"FUNCTION\"";
        s += ">";
        s += (*ite1).second.operation.toString();
        s += "</valeur>\n"; 
      }
      s += "    </implication>\n";
    }
    s += "  </regle>\n\n";
  }
  s += "</univers>";
  FILE *f=fopen(file, "w");
  if (f == NULL) {
    fprintf(stderr,"Erreur dans l'ouverture du fichier");
  }
  else {
    fprintf(f,s.data());
  }
  fclose(f);
  
}

bool checkCurrentTag(xmlTextReaderPtr reader, const char *TAG, int nodetype){
  const xmlChar *name = xmlTextReaderConstName(reader);
  int nt = xmlTextReaderNodeType(reader);
  if (name == NULL)
    name = BAD_CAST "--";
  return (strcmp((char*) name, TAG)==0 && nodetype == nt);
} 

GivenState readGivenState(xmlTextReaderPtr reader, const char *given_state_tag, int mode){
  GivenState s;
  int ret;
  char *name,*action,*option,*value;
  while (!checkCurrentTag(reader,given_state_tag,15)){                
    ret = xmlTextReaderRead(reader);                
    if (checkCurrentTag(reader,OBJECT_TAG,1)){
      ret = xmlTextReaderRead(reader);                  
      assert(!xmlTextReaderIsEmptyElement(reader) && xmlTextReaderHasValue(reader));
      name = (char *)xmlTextReaderConstValue(reader);
      if (mode == 1) printf("name : %s\n", name);
      s.object = name;
    }
    else if (checkCurrentTag(reader,ACTION_TAG,1)){
      ret = xmlTextReaderRead(reader);
      assert(!xmlTextReaderIsEmptyElement(reader) && xmlTextReaderHasValue(reader));
      action = (char *)xmlTextReaderConstValue(reader);
      if (mode == 1) printf(" action: %s\n", action);
      s.state = action;
      s.operation.operation_type = ACTION;
    }
    else if (checkCurrentTag(reader,STATE_TAG,1)){
      ret = xmlTextReaderRead(reader);
      assert(!xmlTextReaderIsEmptyElement(reader) && xmlTextReaderHasValue(reader));
      option = (char *)xmlTextReaderConstValue(reader);
      if (mode == 1) printf(" etat : %s\n", option);
      s.state = option;
    }
    else if (checkCurrentTag(reader,VALUE_TAG,1)){
      char *type = (char *) xmlTextReaderGetAttribute(reader, (xmlChar *)TYPE_ATTR);

      ret = xmlTextReaderRead(reader);
      assert(!xmlTextReaderIsEmptyElement(reader) && xmlTextReaderHasValue(reader));

      value = (char *)xmlTextReaderConstValue(reader);
      if (type != NULL && strcmp(type,"FUNCTION")==0){
        s.operation = createOperation(value);
      }
      else 
        s.operation = Operation(value, STRING);     // JE DIS STRING MAIS C'EST PAS SUR, JE CORRIGE APRES EN CAS
      if (mode == 1) printf(" value : %s\n", value);
      
    }
  }
  return s;
}


/**
 * @brief Constructeur d'Universe
 * 
 * Fonction qui lit un fichier xml et crée un objet Universe
 * @param file le nom de fichier de sauvegarde
 * @param mode 1 verbeux, 0 silencieux
 */

Universe::Universe(const char *file, int mode){
 
  xmlTextReaderPtr reader;
  char *name,*value,*image,*Class,*state,*option,*defaut,*action, *x,*y,*z,*type;

  LIBXML_TEST_VERSION
      int ret;
  filename = string(file); 
  reader = xmlReaderForFile(file, NULL, 0);
  if (reader != NULL) {
    ret = xmlTextReaderRead(reader);
    while (ret == 1){
      if (checkCurrentTag(reader,OBJECT_TAG,1)){
        Object o;
        Class = (char *) xmlTextReaderGetAttribute(reader, (xmlChar *)OBJECT_CLASS_ATTR);
        if (mode == 1) printf("classe : %s\n", Class);
        o.Class = Class;
        vector<State> states;
        vector<Point2di> geometry;
        set<string> actions;
        while (!checkCurrentTag(reader,OBJECT_TAG,15)){            
          ret = xmlTextReaderRead(reader);
          if (checkCurrentTag(reader,STATE_TAG,1)){
            state = (char *) xmlTextReaderGetAttribute(reader, (xmlChar *)STATE_NAME_ATTR);
            if (mode == 1) printf(" etat : %s\n", state);              
            State s;
            s.name = state;
            while (!checkCurrentTag(reader,STATE_TAG,15)){                
              ret = xmlTextReaderRead(reader);                
              if (checkCurrentTag(reader,OPTION_TAG,1)){
                ret = xmlTextReaderRead(reader);                  
                assert(!xmlTextReaderIsEmptyElement(reader) && xmlTextReaderHasValue(reader));
                option = (char *)xmlTextReaderConstValue(reader);
                if (mode == 1) printf(" option : %s\n", option);
                s.options.insert(option);
              }
              else if (checkCurrentTag(reader,VALUE_TAG,1)){
                type = (char *) xmlTextReaderGetAttribute(reader, (xmlChar *)TYPE_ATTR);
                if (strcmp(type, STRING_ATTR) == 0) s.type = STRING;
                else if (strcmp(type, INTEGER_ATTR) == 0) s.type = INTEGER;
                else if (strcmp(type, FLOAT_ATTR) == 0) s.type = FLOAT;
                else if (strcmp(type, BOOLEAN_ATTR) == 0) s.type = BOOLEAN;
                ret = xmlTextReaderRead(reader);
                assert(!xmlTextReaderIsEmptyElement(reader) && xmlTextReaderHasValue(reader));
                defaut = (char *)xmlTextReaderConstValue(reader);
                if (mode == 1) printf(" valeur : %s\n", defaut);
                s.value = defaut;
              }
            }            
            o.states[(const char*)s.name.data()] = s;
          }
          else if (checkCurrentTag(reader,GEOMETRY_TAG,1)){
            name = (char *) xmlTextReaderGetAttribute(reader, (xmlChar *)STATE_NAME_ATTR);
            vector<Point3di> geom_aux;
            while (!checkCurrentTag(reader,GEOMETRY_TAG,15)){
              ret = xmlTextReaderRead(reader);                
              if (checkCurrentTag(reader,POINT_TAG,1)){
                x = (char *) xmlTextReaderGetAttribute(reader, (xmlChar *)POINT_ABSCISSA_ATTR);
                if (mode == 1) printf(" abscisse : %d\n", atoi(x));
                y = (char *) xmlTextReaderGetAttribute(reader, (xmlChar *)POINT_ORDINATE_ATTR);
                if (mode == 1) printf(" ordonnée : %d\n", atoi(y));
                z = (char *) xmlTextReaderGetAttribute(reader, (xmlChar *)POINT_DEPTH_ATTR);
                if (mode == 1) printf(" profondeur : %d\n", atoi(z));
                Point3di p;
                p[0]=atoi(x); p[1]=atoi(y); p[2]=atoi(z);
                geom_aux.push_back(p);
              }
            }
            o.geometries[name] = Vector<Point3di,4>(geom_aux);
          }
          else if (checkCurrentTag(reader,POSITION_TAG,1)){
//             while (!checkCurrentTag(reader,POSITION_TAG,15)){
//               ret = xmlTextReaderRead(reader);                
//               if (checkCurrentTag(reader,POINT_TAG,1)){
                x = (char *) xmlTextReaderGetAttribute(reader, (xmlChar *)POINT_ABSCISSA_ATTR);
                if (mode == 1) printf(" POSITION abscisse : %d\n", atoi(x));
                y = (char *) xmlTextReaderGetAttribute(reader, (xmlChar *)POINT_ORDINATE_ATTR);
                if (mode == 1) printf(" POSITION ordonnée : %d\n", atoi(y));
                z = (char *) xmlTextReaderGetAttribute(reader, (xmlChar *)POINT_DEPTH_ATTR);
                if (mode == 1) printf(" POSITION profondeur : %d\n", atoi(z));
                o.states["POSITION_ABSCISSA"] = State("POSITION_ABSCISSA", "INTEGER", x);
                o.states["POSITION_ORDINATE"] = State("POSITION_ORDINATE", "INTEGER", y);
                o.states["POSITION_DEPTH"] = State("POSITION_DEPTH", "INTEGER", z);
//               }
//             }
          }
          else if (checkCurrentTag(reader,NAME_TAG,1)){
            ret = xmlTextReaderRead(reader);
            assert(!xmlTextReaderIsEmptyElement(reader) && xmlTextReaderHasValue(reader));
            name = (char *)xmlTextReaderConstValue(reader);
            if (mode == 1) printf(" name : %s\n", name);              
            o.name = name;
          }
          else if (checkCurrentTag(reader,ACTION_TAG,1)){
            ret = xmlTextReaderRead(reader);
            assert(!xmlTextReaderIsEmptyElement(reader) && xmlTextReaderHasValue(reader));
            action = (char *)xmlTextReaderConstValue(reader);
            if (mode == 1) printf(" action : %s\n", action);
            o.actions.insert(action);
          }
        }
          // stockage de l'objet 
        objects[o.name.data()] = o;        
      }
      else if (checkCurrentTag(reader,RULE_TAG,1)){
        vector<GivenState> conditions;
        vector<GivenState> implications;
          
        while (!checkCurrentTag(reader,RULE_TAG,15)){            
          ret = xmlTextReaderRead(reader);
          if (checkCurrentTag(reader,CONDITION_TAG,1)){
            GivenState cond(readGivenState(reader, CONDITION_TAG, mode));
            if (cond.object != "SYSTEM" && cond.operation.operation_type == SCALAR){
            
              uint type = objects[cond.object.data()].states[cond.state.data()].type;   // SOUS-ENTENDU DONC QUE L'OBJET A DEJA ETE LU ET STOCKE
              cond.operation.data_type = type;
            }
            conditions.push_back(cond);
          }
          else if (checkCurrentTag(reader,IMPLICATION_TAG,1)){
            GivenState impl(readGivenState(reader, IMPLICATION_TAG, mode));
            if (impl.object != "SYSTEM" && impl.operation.operation_type == SCALAR){
              
              uint type = objects[impl.object.data()].states[impl.state.data()].type;   // SOUS-ENTENDU DONC QUE L'OBJET A DEJA ETE LU ET STOCKE
              impl.operation.data_type = type;
            }
            implications.push_back(impl);
          }
        }
          // stockage de la règle 
        rules.push_back(*(new Rule(conditions,implications)));
      }
      ret = xmlTextReaderRead(reader);
    }  
//     sortDisplayable();
  } else {
    fprintf(stderr, "Unable to open %s\n", file);
  }
  xmlCleanupParser();
  xmlMemoryDump();


  
}

/**
 * @brief Détermine si une condition est remplie, en la comparant avec un triplet nom/état/valeur donné. 
 * 
 * @param condition la condition à vérifier
 * @param name le nom à comparer
 * @param etat le nom de l'état à comparer
 * @param valeur la valeur à comparer
 * @return le retour de la fonction.
 */

bool isRemplieCondition(GivenState &condition, string &name, string &etat, string &valeur){
  bool resultat = true;
  if (valeur != "[action]"){
    resultat = (condition.object == name && condition.state == etat && condition.operation.value == valeur);
  }
  else{
    resultat = (condition.object == name && condition.state == etat);
  }
  return resultat;
}

/**
 * @brief A partir d'une rule et d'une liste des actions courantes, détermine si les conditions sont satisfaites par l'univers + les actions
 * 
 * @param r la règle à vérifier
 * @param actions les actions courantes
 * @return true si la règle est vérifiée, false sinon
 */

bool Universe::isRempliesConditionsRegleWithActions(Rule &r, vector<GivenState> &actions){
  bool resultat = true;
  uint ii=0;
  bool test;
  map<const char *, Object, ltstr>::iterator ite;
  map<const char *, State, ltstr>::iterator iter;
  multimap<const char *, GivenState, ltstr>::iterator ite1;
  for (ite1=r.conditions.begin();ite1!=r.conditions.end();ite1++){
    if ((*ite1).second.operation.operation_type != ACTION){
      ii++;
      test = false;
      for (ite=objects.begin();ite!=objects.end();ite++){
        for (iter=(*ite).second.states.begin();iter!=(*ite).second.states.end();iter++){
          if (isRemplieCondition((*ite1).second, (*ite).second.name, (*iter).second.name, (*iter).second.value))
            test = true;
          if (test) break;
        }
        if (test) break;
      }
      if (!test) resultat = false;
    }
    else {
      test = false;
      for (uint j=0;j<actions.size();j++){
        if (isRemplieCondition((*ite1).second, actions[j].object, actions[j].state, actions[j].operation.value))
          test = true; 
      }
      if (!test) resultat = false;
    }
    if (!resultat) break;
  }
  if (ii==0 && actions.size() == 0) resultat = false;
  return resultat;
}

/**
 * @brief Détermine les règles dont les conditions sont satisfaites par les états de l'univers + les actions courantes
 * 
 * @param actions les actions courantes
 * @return les règles dont les conditions sont satisfaites
 */

vector<uint> Universe::satisfiedConditionsRulesWithActions(vector<GivenState> &actions){
  vector<uint> satisfied;
  for (uint i=0;i<actions.size();i++){
    if (actions[i].object == "SYSTEM"){
      if (actions[i].state == "PRINT"){
        printf("SYSTEM : %s\n", actions[i].operation.value.data());
      }
    }
    else if (objects[actions[i].object.data()].Class == "Timer"){
      if (actions[i].state == "Run"){
        int index = 0;
        for (index=0;index<timers.size() && objects[actions[i].object.data()].name.data() == timers[index];index++);
        glutTimerFunc(atoi(objects[actions[i].object.data()].states["INTERVAL"].value.data()),Timer,index-1);
      }
    }
  }
  for (uint k=0;k<rules.size();k++)
    if (isRempliesConditionsRegleWithActions(rules[k], actions))
      satisfied.push_back(k);
  return satisfied;
}


/**
 * @brief Dans le cas d'une implication/condition appelant à une opération arithmétique, calcule et renvoit le résultat de cette opération.
 *
 * 
 * @param Operation l'opération à effectuer
 * @return le résultat de l'opération
 */

int Universe::computeOperation(Operation op){
  if (op.operation_type == SCALAR){
    if (op.scalar_type == CONSTANT){
      if (op.data_type == INTEGER)
        return atoi(op.value.data());
    }
    else if (op.scalar_type == VARIABLE){
      return atoi(objects[op.object.data()].states[op.state.data()].value.data());
    }
  }
  else if (op.operation_type == OPERATION){
    if (op.f == "AJOUTE")
      return computeOperation(op.op[0]) + computeOperation(op.op[1]);
    else if (op.f == "SOUSTRAIT")
      return computeOperation(op.op[0]) - computeOperation(op.op[1]);
    else if (op.f == "OPPOSE")
      return - computeOperation(op.op[0]);
  }
}

/**
 * @brief Applique les implications des règles dont les conditions sont satisfaites
 *
 * 
 * @param implication l'implication de la règle dont les conditions sont satisfaites
 * @return true s'il y a eu changement dans l'univers, false sinon
 */

bool Universe::applyImplication(GivenState &implication){
  map<const char *, Object, ltstr>::iterator ite;
  map<const char *, State, ltstr>::iterator iter;
  ite = objects.find(implication.object.data());
  if (ite != objects.end()){
    iter = (*ite).second.states.find((const char*) implication.state.data()); 
    if (iter != (*ite).second.states.end()){
      if (implication.operation.operation_type == SCALAR){
        printf("SCALAR\n");
        if (implication.operation.scalar_type == CONSTANT){
          if ((*iter).second.value != implication.operation.value) {
            (*iter).second.value = implication.operation.value;
            return true;
          }
          else {
            return false;
          }
        }
        else if (implication.operation.scalar_type == VARIABLE){
          printf("VARIABLE\n");
          string value = objects[implication.operation.object.data()].states[implication.operation.state.data()].value;
          if ((*iter).second.value != value){
            (*iter).second.value = value;
            return true;
          }
          else {
            return false;
          }
        }
      }
      else if (implication.operation.operation_type == OPERATION){
        printf("OPERATION\n");
        int result = computeOperation(implication.operation);
        printf("%d\n", result);
        char buffer[5];
        sprintf(buffer, "%d", result);
        string value = buffer;
        if ((*iter).second.value != value){
          (*iter).second.value = value;
          return true;
        }
        else {
          return false;
        }
      } 
   
    }
  }
}

/**
 * @brief Mise à jour des états de l'univers
 * 
 * Mise à jour des états de l'univers : on vérifie les conditions des règles qui sont remplies, par rapport aux actions en cours, et on applique les implications. On recommence le processus tant qu'il y a des changements dans les implications. 
 * @param actions les actions en cours
 * @param verbose 1 pour afficher l'univers après mise-à-jour, 0 pour rien du tout
 * @param save 1 pour sauvegarder l'univers sur le disque dans son fichier associé après mise-à-jour, 0 pour rien du tout
 * @return met à jour l'univers
 */

void Universe::update(vector<GivenState> &actions, uint verbose, uint save){
  bool loop = true;
  multimap<const char *, GivenState, ltstr>::iterator ite1;
  vector<GivenState> newactions;
  vector<GivenState> allactions(actions);
  vector<uint> satisfaites;
  bool testActionSystem;  
  while (loop){
    loop = false;
    newactions.clear();
    satisfaites = satisfiedConditionsRulesWithActions(actions);
    for (uint k=0;k<satisfaites.size();k++){
      multimap<const char *, GivenState, ltstr> implications(rules[satisfaites[k]].implications);
      for (ite1=implications.begin();ite1!=implications.end();ite1++){
        bool already = false;
        testActionSystem = false;
        if ((*ite1).second.operation.operation_type == ACTION){ // ON CHERCHE A SAVOIR SI L'ACTION A DEJA ETE EFFECTUEE
          testActionSystem = true; 
          for (uint i=0; i<allactions.size() && !already ; i++){
            if (allactions[i].object == (*ite1).second.object && allactions[i].state == (*ite1).second.state)
              already = true;
          }
        }
        else if ((*ite1).second.object == "SYSTEM"){ // MEME CHOSE POUR LES ACTIONS "SYSTEM"
          testActionSystem = true;
          for (uint i=0; i<allactions.size() && !already ; i++){
            if (allactions[i].object == "SYSTEM" && allactions[i].state == (*ite1).second.state && allactions[i].operation.value == (*ite1).second.operation.value)
              already = true;
          } 
        }
        if (testActionSystem){   // S'IL Y A EU UNE ACTION, ET QU'ELLE N'A PAS ENCORE ETE REALISEE ALORS ON LA RAJOUTE A LA LISTE COMPRENANT TOUTES LES ACTIONS EFFECTUEES ET CELLE DES NOUVELLES ACTIONS
          if (!already){
            allactions.push_back((*ite1).second);
            newactions.push_back((*ite1).second);
            loop = true;
          }
        }
        else {
          if (applyImplication((*ite1).second)){  // APPLIQUE LES IMPLICATIONS I.E. CHANGE LES ETATS DES OBJETS CONCERNES
            loop = true; 
          }
        }
      }
    }
    if (loop) actions = *(new vector<GivenState>(newactions));
  }
  printf("UPDATE\n");

  if (verbose == 1){
    map<const char *, Object, ltstr>::iterator ite;
    for (ite=objects.begin();ite!=objects.end();ite++){
      printf("%s\n\n", (*ite).second.toString());
    }
  }

  if (save == 1)
    saveToDisk(filename.data());

}

/** 
 * @brief Renvoit les objets dont le champ classe est égal à la chaine classe passé en paramètre
 *
 * @param classe la classe en question
 * @return une map des objets
 */

map<const char*,  Object *, ltstr> Universe::getObjectsOfClass(const char *classe){
  map<const char *, Object, ltstr>::iterator ite;
  map<const char *, Object*, ltstr> result;
  for (ite=objects.begin();ite!=objects.end();ite++){
    if (strcmp((*ite).second.Class.data(), classe)==0){
      Object *o = &((*ite).second);
      result[(*ite).second.name.data()] = o;
    }
  }
  return result;
}



void Universe::RegisterTimers(){
  map<const char*,Object *,ltstr>::iterator it;
  map<const char*,Object *,ltstr> tim(getObjectsOfClass("Timer"));
  for (it = tim.begin();it!=tim.end();it++){
    timers.push_back((*it).first);
  }
}







