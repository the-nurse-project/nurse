
LDFLAGS = -lm -lpng -L/usr/X11R6/lib -lglut -lGLU -lGL -lX11 -lXmu -lXext -lXi

CFLAGS = -Wno-deprecated

XMLFLAGS = `xml2-config --cflags` 

OBJ = objects/
SRC = sources/

all: main

clean:
	rm $(OBJ)*.o
   
main: $(OBJ)main.o 
	g++ `xml2-config --cflags --libs` $(OBJ)*.o $(LDFLAGS) $(CFLAGS)

$(OBJ)main.o : $(SRC)main.cc $(OBJ)universe.o
	g++ -c $(SRC)main.cc -o $(OBJ)main.o $(CFLAGS) $(XMLFLAGS)

$(OBJ)object.o : $(SRC)object.cc $(OBJ)rule.o $(OBJ)image.o $(SRC)object.h
	g++ -c $(SRC)object.cc -o $(OBJ)object.o $(CFLAGS) $(XMLFLAGS)

$(OBJ)universe.o : $(SRC)universe.cc $(OBJ)object.o $(OBJ)operation.o $(SRC)universe.h $(SRC)vector.h $(SRC)timer.h 
	g++ -c $(SRC)universe.cc -o $(OBJ)universe.o $(CFLAGS) $(XMLFLAGS)

$(OBJ)rule.o : $(SRC)rule.cc $(OBJ)operation.o $(SRC)rule.h
	g++ -c $(SRC)rule.cc -o $(OBJ)rule.o $(CFLAGS) $(XMLFLAGS)

$(OBJ)image.o : $(SRC)image.cc $(OBJ)png_tex.o $(SRC)png_tex.h $(SRC)image.h $(SRC)vector.h
	g++ -c $(SRC)image.cc -o $(OBJ)image.o $(CFLAGS)

$(OBJ)png_tex.o : $(SRC)png_tex.c $(SRC)png_tex.h
	g++ -c $(SRC)png_tex.c -o $(OBJ)png_tex.o $(CFLAGS)
	
$(OBJ)operation.o : $(SRC)operation.cc $(SRC)operation.h
	g++ -c $(SRC)operation.cc -o $(OBJ)operation.o $(CFLAGS)
	
# $(OBJ)Model.o : $(SRC)Model.cpp $(SRC)Model.h
# 	g++ -c $(SRC)Model.cpp -o $(OBJ)Model.o $(CFLAGS)
	
# model : $(SRC)model.cc $(SRC)model.h
# 	g++ $(SRC)model.cc -o a.out $(CFLAGS) $(LDFLAGS)