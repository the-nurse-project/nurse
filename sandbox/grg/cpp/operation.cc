

#include "operation.h"

// Opnode



Operation createOperation(const string &input){
//   printf("%s\n", input.data());
//   string::iterator it;                   // pour virer tous les espaces de la chaîne...
//   for (it=input.begin();it!=input.end();)
//     if ((*it)==' ') input.erase(it);
//     else it++;
//   printf("%s\n",input.data());
  int dot = input.find(".",0);
  int par = input.find("(",0);
  
  if (input[0]>47 && input[0]<58){ //si c'est un chiffre (on peut alors supposer que c'est un scalaire)
    
//     printf("ajout scalaire : %d\n", atoi(input.data()));

    return Operation(input.data(), INTEGER);
  }
  else if ( par != -1){
//     printf("\nsous-fonction:\n");
    unsigned int depth=0;
    depth++;
    unsigned int parEnd = par;
    int comma = par;
    while (depth!=0){
      parEnd++;    
      if (input[parEnd] == '(') depth++;
      else if (input[parEnd] == ')') depth--;
      else if (input[parEnd] == ',' && depth == 1) comma = parEnd;
    }
    Operation result;
    result.f = input.substr(0,par);  
//     printf("nom fonction : %s\n",result.f.data());
    
    string sub= input.substr(par+1, parEnd-par-1);
//     printf(" argument : %s\n", sub.data());
    if (comma == par)  {//operation unaire
    // on détermine si c'est un nombre, si c'est une variable, ou si c'est une opération
//       printf("\n");
      result.op.push_back(createOperation(sub));
    }
    else { //operation binaire
      string part1 = input.substr(par+1,comma-par-1);
      string part2 = input.substr(comma+1, parEnd-comma-1);
//       printf("  %s %s\n", part1.data(), part2.data());
      result.op.push_back(createOperation(part1));
//       printf("\n");
      result.op.push_back(createOperation(part2));
    }
    return result;
  }
  else if ( dot != -1){ // si ya un point c'est que c'est une variable
//     printf("  variable :\n");
    string a = input.substr(0,dot);
    string b = input.substr(dot+1,input.size()-dot-1);
    assert(!(a.empty() || b.empty()));
//     printf("  %s . %s\n", a.data(), b.data());
    return Operation(a,b, INTEGER);
  }
  else printf("LOL\n");
  // principe:
  // on traite les deux bouts segmentés : par+1 -> comma-1, comma+1 -> parEnd
  // premier bout :
   // si le bout est un nombre, Scalar(le nombre) puis push_back Scalar dans result.op
   // si le bout contient un "." c'est une variable, donc Scalar(object,state) puis push_back dans result.op
   // si le bout contient une parenthèse "(", on remplit le nom de la fonction puis on détermine ses "," et ")" correspondants
       // et on relance l'algo pour ces deux sous-bouts (l'algo devant renvoyer un Operation)
  // deuxième bout :
    // même chose
  Operation test(1);
  return test;
}

const string Operation::toString(void){
  
  if (operation_type==ACTION){
    return "[action]";
  }
  else if (operation_type == SCALAR){
    if (scalar_type == CONSTANT){
      return value;
    }
    else if (scalar_type == VARIABLE){
      string tmp(object);
      tmp += ".";
      tmp += state;
      return tmp;
    }
  }
  else if (operation_type == OPERATION){
    string tmp(f);
    tmp += "(";
    if (op.size()==1){
      tmp += op[0].toString();
    }
    else{
      tmp += op[0].toString();
      tmp += ",";
      tmp += op[1].toString();
    }
    tmp += ")";
    return tmp;
  }
  
  
  
  
}

// int main(void){
//   string input = "ajouter(soustraire(test.caca),multiplier(3))";
//   Operation op = createOperation(input);
//   printf("======================\n");
//   printf("%s\n", op.toString().data());
//   
//   
//   return 0; 
// }
