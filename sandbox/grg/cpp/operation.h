

#ifndef __OPERATION_H__
#define __OPERATION_H__

#include <vector>
#include <string>
#include <set>
#include <assert.h>
#include <stdio.h>

using namespace std;

enum {SCALAR, OPERATION, ACTION};
enum {CONSTANT, VARIABLE};
enum {INTEGER, FLOAT, STRING, BOOLEAN};


class Operation{
  public:
    unsigned int operation_type;
    unsigned int scalar_type;
    unsigned int data_type;
    string value;
    string object;
    string state;
    string f;
    vector< Operation > op;
    Operation( string s, unsigned int i ){ operation_type = SCALAR; scalar_type = CONSTANT; data_type = i; value = s; }
    Operation( int v ){ operation_type = SCALAR; scalar_type = CONSTANT; data_type = INTEGER; char buffer[5]; sprintf(buffer,"%d",v); value = string(buffer); }
    Operation( string o, string s, unsigned int i ){ operation_type = SCALAR;
      scalar_type = VARIABLE; data_type = i; object = o; state = s; }
    Operation( void ){ operation_type=OPERATION; }
    const string toString( void );
};

Operation createOperation(const string &input);


#endif
