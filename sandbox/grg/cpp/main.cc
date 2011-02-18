#include <GL/glut.h>
#include <iostream> 
#include <cstdlib>
// #include <lib3ds/mesh.h>
// #include <lib3ds/file.h>
// #include "Model.h"

#include "universe.h"


unsigned int WINDOWWIDTH = 1000;
unsigned int WINDOWHEIGHT = 900;

Universe u;
GLubyte *N;
float alpha=0.0;
int X=0, Y=0, Z=0;
map<const char*,unsigned int,ltstr> TextIndex;
GLuint *NomsTextures;
GLuint *NomsTextures2;
unsigned int temps=0;
unsigned int mouseX, mouseY;
Image2D<unsigned char> pickingBuffer;


void keyboard (unsigned char key, int x, int y)
{
  switch (key)
    {
    case 'p':       X++; break;
    case 'o':      X--; break;
    case 'i':      Z++; break;
    case 'k':      Z--; break;
    case 'a':      alpha = alpha-0.5; break;
    case 'z':      alpha = alpha+0.5; break;
    case 27: /* escape */      exit(0);      break;
    }
  printf("%d %d %.d %.3f\n", X, Y, Z, alpha);

glutPostRedisplay();
}

int pickObject(int x,int y){
//   resize(WINDOWWIDTH,WINDOWHEIGHT);
//   setCamera();
  glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT );

  map<const char *, Object, ltstr>::iterator itera;
  map<const char *, State, ltstr>::iterator iter;
  string current_image;
//     glDrawBuffer(GL_FRONT);
  unsigned int index=0;
  glClearColor(0,0,0,0);
  glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT );
  glTexEnvi( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE);
//     GLint rgba[4]={0,0,0,0};
//     glTexEnviv( GL_TEXTURE_ENV, GL_TEXTURE_ENV_COLOR, rgba);
  glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);

  glEnable(GL_TEXTURE_2D);
  glEnable(GL_BLEND);
  for (itera = u.objects.begin();  itera != u.objects.end(); itera++){
    index = index + 1;
    iter = (*itera).second.states.find("VISIBLE");  
    if (iter == (*itera).second.states.end() || (*iter).second.value == "TRUE"){
      iter = (*itera).second.states.find("CURRENT_IMAGE"); 
      if (iter == (*itera).second.states.end())
        current_image = "default";
      else
        current_image = (*iter).second.value;
      Point3di position;
      Vector<Point3di,4> quad((*itera).second.geometries["default"]);
      assert((*itera).second.getPosition(position));
        
      glBindTexture(GL_TEXTURE_2D,NomsTextures2[TextIndex[u.objects[current_image.data()].states["FILE"].value.data()]]);

      glBegin (GL_QUADS);
      glColor4ub(index,0,0,255);
      glTexCoord2f (0.0f, 0.0f);
      glVertex3f (position[0]+quad[0][0],position[1]+quad[0][1], position[2]+quad[0][2]);
    
      glTexCoord2f (1.0f, 0.0f);
      glVertex3f (position[0]+quad[1][0],position[1]+quad[1][1], position[2]+quad[1][2]);

      glTexCoord2f (1.0f, 1.0f);
      glVertex3f (position[0]+quad[2][0],position[1]+quad[2][1], position[2]+quad[2][2]);

      glTexCoord2f (0.0f, 1.0f);
      glVertex3f (position[0]+quad[3][0],position[1]+quad[3][1], position[2]+quad[3][2]);
      glEnd();

    }
  }
  glDisable(GL_BLEND);
  glDisable(GL_TEXTURE_2D);
  GLubyte *test = new GLubyte;
  glReadBuffer(GL_BACK);
  glReadPixels(x,y,1,1,GL_RED,GL_UNSIGNED_BYTE,test);
  glClearColor(0.5,0.5,0.5,0.5);

  return (int)*test;
}

void InitTex(map<const char*,unsigned int,ltstr> &textures)
{ 	
  map<const char*,unsigned int,ltstr>::iterator it;

  for (it = textures.begin();it!=textures.end();it++){
  
    glBindTexture(GL_TEXTURE_2D,NomsTextures[(*it).second]); 	//Sélectionne ce n°
    
    GLubyte *text,*text2;
    Image2DColor im;
    im.ReadImagePNG((*it).first);
    text = (GLubyte *)malloc(im.width*im.height*4 * sizeof(GLubyte));
    text2 = (GLubyte *)malloc(im.width*im.height*4 * sizeof(GLubyte));
    
    im.BasculeImage(text);
    

    glTexImage2D (
                  GL_TEXTURE_2D, 	//Type : texture 2D
                  0, 	//Mipmap : aucun
                  4, 	//Couleurs : 4 (R G B A)
                  im.width, 	//Largeur : 2
                  im.height, 	//Hauteur : 2
                  0, 	//Largeur du bord : 0
                  GL_RGBA, 	//Format : RGBA
                  GL_UNSIGNED_BYTE, 	//Type des couleurs
                  text 	//Addresse de l'image
                ); 	
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    free(text);
    for (unsigned int i=0;i<im.width;i++)
      for (unsigned int j=0;j<im.height;j++){
        im[j][i][0]=im[j][i][1]=im[j][i][2]=255;
        if (im[j][i][3] < 255) im[j][i][3]=0;
      }
    im.BasculeImage(text2);
    glBindTexture(GL_TEXTURE_2D,NomsTextures2[(*it).second]);
    glTexImage2D (
                  GL_TEXTURE_2D, 	//Type : texture 2D
                  0, 	//Mipmap : aucun
                  4, 	//Couleurs : 4 (R G B A)
                  im.width, 	//Largeur : 2
                  im.height, 	//Hauteur : 2
                  0, 	//Largeur du bord : 0
                  GL_RGBA, 	//Format : RGBA
                  GL_UNSIGNED_BYTE, 	//Type des couleurs
                  text2 	//Addresse de l'image
                 ); 	
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    free(text2);
    
  }
} 	


void render_string(float x, float y, void* font, const char* s)
{
  glRasterPos2f(x, y);
  while(*s){
    glutBitmapCharacter(font, *s);
    s++;
  }
}


//     Model model;

//Oui il faudrait non pas charger les textures dans le display mais faire ça au tout début, lors du chargement des objets, une fois pour toutes. Au début on chargerait toutes les textures de l'univers (dans une map<string,map<string,index> > qui associe un index("Nom") de texture au nom de l'objet et au nom de l'image en question)

void display(void){

  glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT );

  glMatrixMode(GL_MODELVIEW) ;
  glLoadIdentity();
  gluLookAt(0,0,0,0,0,-10,0,1,0);  
//   glTranslatef(X,Y,Z);
//   glRotatef(alpha, 0.0,1.0,0.0);
  
//   printf("TRANSF : %.3f %.3f %.3f %.3f\n", X, Y, Z, alpha);
  
  map<const char *, Object, ltstr>::iterator ite;
  map<const char *, State, ltstr>::iterator iter;
  string current_image;
  glTexEnvi( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE);
  glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);

  glEnable(GL_TEXTURE_2D);
  glEnable(GL_BLEND);
  glEnable(GL_DEPTH_TEST);
  for (ite = u.objects.begin(); ite != u.objects.end(); ite++){
    iter = (*ite).second.states.find("VISIBLE"); 
    if (iter == (*ite).second.states.end() || (*iter).second.value == "TRUE"){ 
      iter = (*ite).second.states.find("CURRENT_IMAGE");  
      if (iter == (*ite).second.states.end())
        current_image = "default";
      else
        current_image = (*iter).second.value;
      
      glBindTexture(GL_TEXTURE_2D,NomsTextures[TextIndex[u.objects[current_image.data()].states["FILE"].value.data()]]);
      glBegin (GL_QUADS);
    
      Point3di position;
      Vector<Point3di,4> quad((*ite).second.geometries["default"]);
      assert((*ite).second.getPosition(position));

      glTexCoord2f (0.0f, 0.0f);
      glVertex3f (position[0]+quad[0][0],position[1]+quad[0][1], position[2]+quad[0][2]);
    
      glTexCoord2f (1.0f, 0.0f);
      glVertex3f (position[0]+quad[1][0],position[1]+quad[1][1], position[2]+quad[1][2]);

      glTexCoord2f (1.0f, 1.0f);
      glVertex3f (position[0]+quad[2][0],position[1]+quad[2][1], position[2]+quad[2][2]);

      glTexCoord2f (0.0f, 1.0f);
      glVertex3f (position[0]+quad[3][0],position[1]+quad[3][1], position[2]+quad[3][2]);
      glEnd();
    }
  }
  glDisable(GL_BLEND);
  glDisable(GL_TEXTURE_2D);
  glDisable(GL_DEPTH_TEST);
//   model.draw();
  char buffer[10];
  sprintf(buffer, "%s", u.objects["libertad"].states["VISIBLE"].value.data());
  glColor4f(1.0,1.0,1.0,0.0);
  render_string(100,100,GLUT_BITMAP_HELVETICA_18, buffer);
  glutSwapBuffers();  

}


void resize(int w, int h){
  WINDOWWIDTH = w;
  WINDOWHEIGHT = h;
  glMatrixMode(GL_MODELVIEW); 
  glLoadIdentity();
  glViewport(0,0,w,h);
  glMatrixMode(GL_PROJECTION);
  glLoadIdentity();
  glOrtho(0,w,0,h,-100,100);
//   gluPerspective(45.0f,(GLfloat)w/(GLfloat)h,1.0f,1000.0f);
}

void mouse(int button, int state, int x, int y){
  map<const char *, Object, ltstr>::iterator ite;

  if (state == GLUT_DOWN){
    printf("%d %d ====================================================\n", x,y); 
    map<const char *, Object, ltstr>::iterator itera;
    unsigned char test = pickObject(x,WINDOWHEIGHT-1-y); //pickingBuffer[WINDOWHEIGHT-1-y][x];
    temps = test;
    if (test>0){
      vector<GivenState> actions;
      unsigned int aux=1;
      for (itera = u.objects.begin();aux<test; itera++, aux++);
      actions.push_back(*new GivenState((*itera).first, "clique"));
      printf("action : %s %s\n", actions[0].object.data(), actions[0].state.data());
      u.update(actions, 1, 1);
    }
    glutPostRedisplay();
  }
}

void motion(int x, int y){

  if (y<WINDOWHEIGHT && x<WINDOWWIDTH){
    mouseX = x;
    mouseY = y;
    temps = pickObject(x,WINDOWHEIGHT-1-y); //pickingBuffer[WINDOWHEIGHT-1-y][x];
    glutPostRedisplay();
  }
}

void Timer(int index){

  if (u.objects[u.timers[index]].states["RUNNING"].value == "TRUE"){
    if (u.objects[u.timers[index]].states["TYPE"].value == "RECURRENT"){
      glutTimerFunc(atoi(u.objects[u.timers[index]].states["INTERVAL"].value.data()), Timer, index);
    }

    vector<GivenState> actions;
    actions.push_back(*new GivenState(u.timers[index], "Tick"));
    printf("action : %s %s\n", actions[0].object.data(), actions[0].state.data());

    if (u.objects[u.timers[index]].states["TYPE"].value == "SINGLE"){
      actions.push_back(*new GivenState(u.timers[index], "Stop"));
      printf("action : %s %s\n", actions[0].object.data(), actions[0].state.data());
    }
    u.update(actions, 1, 1);
    glutPostRedisplay();
  }
}



int main(int argc, char **argv) {
    u = *new Universe("data/test_scenario.xml");
    map<const char *, Object, ltstr>::iterator ite;
    map<const char *, Object*,ltstr>::iterator it;

    printf("\n");
    
    vector<GivenState> actions;
    if (argc == 3){
      actions.push_back(*new GivenState((string)argv[1], (string)argv[2]));
    }
    u.update(actions,1,1);


    glutInit(&argc,argv);
    glPixelStorei ( GL_UNPACK_ALIGNMENT,  1 ); 

    glutInitWindowPosition(0,0);
    glutInitWindowSize(WINDOWWIDTH,WINDOWHEIGHT);
    glutInitDisplayMode(GLUT_RGBA|GLUT_DOUBLE|GLUT_DEPTH);

    glutCreateWindow("Premier essai graphique");
    
    glutDisplayFunc(display);
    glutReshapeFunc(resize);
    glutMouseFunc(mouse);
    glutKeyboardFunc(keyboard);
    glutPassiveMotionFunc(motion);
//     glutSetCursor(GLUT_CURSOR_NONE);
    
    glClearColor(0.5,0.5,0.5,0);

    unsigned int nbtex=0;
    map<const char*, Object *, ltstr> textures(u.getObjectsOfClass("Image"));
    for (it=textures.begin();it!=textures.end();it++)
      TextIndex[(*((*it).second)).states["FILE"].value.data()] = nbtex++;
    
    u.RegisterTimers();
    NomsTextures = (GLuint *) malloc(TextIndex.size()*sizeof(GLuint));
    NomsTextures2 = (GLuint *) malloc(TextIndex.size()*sizeof(GLuint));

    glGenTextures(TextIndex.size(),NomsTextures);
    glGenTextures(TextIndex.size(),NomsTextures2);
    
    InitTex(TextIndex);
    printf(" TEXTURES INDEX : %d\n", TextIndex.size());
    
    printf("%d objets dans la scène\n", u.objects.size());

//     model.loadModelData("Model.ms3d");
    glutMainLoop();

    
    return(0);
}

