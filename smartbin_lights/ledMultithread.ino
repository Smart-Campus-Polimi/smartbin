#include <Adafruit_NeoPixel.h>

#define MAX_BRIGHTNESS      100
#define SPEED_FACTOR          0.08
#define WASTE_RING_SPEED     50
/****** NEOPIXEL CAMERA ******/
#define PIN_CAMERA            6
#define CAMERA_PIXELS        24
/****** NEOPIXEL RING ******/
#define PIN_RING              7
#define RING_PIXELS         162

/****** WASTE RING ******/
#define PIN_UNSORTED          9
#define PIN_PLASTIC           5
#define PIN_PAPER             4
#define PIN_GLASS             3

#define WASTE_RING_PIXELS    60
#define WASTE_FULL_PIXELS     8
#define OFFSET_WASTE          3

/****** MATRIX ******/
#define PIN_MATRIX            8
#define MATRIX_PIXELS        64
/***** ARROW ANIMATION *****/
#define LEG_ARROW             8
#define BRANCH_ARROW          6
#define MAX_ARROW            18
#define MAX_CROSS            13

const int arrow_indices[MAX_ARROW] = {0, 9, 18, 23, 27, 31, 36, 39, 45, 47, 54, 55, 58, 59, 60, 61, 62, 63};
const int cross_indices[MAX_CROSS] = {12,20,28,33,34,35,36,37,38,39,44,52,60};

const int arrowLeg[LEG_ARROW] = {0,9,18,27,36,45,54,63};
const int arrowBranch1[BRANCH_ARROW] = {62, 61, 60, 59, 58, 57};
const int arrowBranch2[BRANCH_ARROW] = {55, 47, 39, 31, 23, 15};




enum  pattern { NONE, STATIC, BLINK, BREATHE, ARROW_ANIMATION, ARROW, CROSS, WASTE, MY_STATIC};
enum  direction { FORWARD, REVERSE };

class NeoPatterns : public Adafruit_NeoPixel
{
  public: 

  pattern ActivePattern;
  direction Direction; 
  unsigned long Interval;
  unsigned long lastUpdate;

  uint32_t Color1; 
  uint16_t TotalSteps; 
  uint16_t Index; 
  uint16_t Jindex;
  uint16_t Prev; 
  uint8_t Level;



  float Intensity, IntensityOld;
  bool First_half = false;

  void (*OnComplete)();  // Callback on completion of pattern

  // Constructor - calls base-class constructor to initialize strip
  NeoPatterns(uint16_t pixels, uint8_t pin, uint8_t type, void (*callback)())
  :Adafruit_NeoPixel(pixels, pin, type)
  {
      OnComplete = callback;
  }

  void Update()
    {
       // if((millis() - lastUpdate) > Interval) // time to update
        //{
            lastUpdate = millis();
            switch(ActivePattern)
            {
                case NONE:
                    //RainbowCycleUpdate();
                    break;
                case STATIC:
                    onStaticUpdate();
                    break;
                case BLINK:
                    //ColorWipeUpdate();
                    break;
                case BREATHE:
                    breatheUpdate();
                    break;
                case ARROW_ANIMATION:
                    turnOff();
                    arrowAnimationUpdate();
                    break;
                case ARROW:
                    turnOff();
                    arrowUpdate();
                    break;
                case CROSS:
                    turnOff();
                    crossUpdate();
                    break;
                case WASTE:
                    //turnOff();
                    wasteUpdate();
                case MY_STATIC:
                    wasteStaticUpdate();
                    break;
                default:
                    break;
            }
       // }
    }


  void IncrementBreathe(){
    IntensityOld = Intensity;
     if (Direction == FORWARD)
        {
           Index++;
           if (Intensity < IntensityOld)
            {
                //Index = 0;
                if (OnComplete != NULL)
                {
                    OnComplete(); // call the comlpetion callback
                }
            }
        }
        else // Direction == REVERSE
        {
            --Index;
            if (Intensity > IntensityOld)
            {
                //Index = TotalSteps-1;
                if (OnComplete != NULL)
                {
                    OnComplete(); // call the comlpetion callback
                }
            }
        }
  }
    
  void Increment()
    {
          if (Direction == FORWARD)
        {
           Index++;
           
           if (Index >= TotalSteps)
            {
                Index = 0;
                if (OnComplete != NULL)
                {
                    OnComplete(); // call the comlpetion callback
                }
            }
        }
        else // Direction == REVERSE
        {
            --Index;
            if (Index <= 0)
            {
                Index = TotalSteps-1;
                if (OnComplete != NULL)
                {
                    OnComplete(); // call the comlpetion callback
                }
            }
        }
    }

    void IncrementRing(uint8_t level)
    {
      
        if(Index < level){
           Index++;
        }
    }

    // Reverse pattern direction
    void Reverse()
    {
        if (Direction == FORWARD)
        {
            Direction = REVERSE;
            Index = TotalSteps-1;
        }
        else
        {
            Direction = FORWARD;
            Index = 0;
        }
    }
    
   /****** STATIC ******/
   void onStatic(uint32_t color1, uint8_t interval)
    {
        ActivePattern = STATIC;
        TotalSteps = 255;
        Index = 0;
        Color1 = color1;
        Interval = interval;
    }

    void onStaticUpdate()
    {
       setBrightness(MAX_BRIGHTNESS);
      for(int i=0; i< numPixels(); i++)
        {
            setPixelColor(i, Color1);
        }
        show();
        //Increment();
    }

    /****** STATIC ******/
   void wasteStatic(uint32_t color1, uint8_t interval, uint8_t level)
    {
        ActivePattern = STATIC;
        TotalSteps = 255;
        Index = 0;
        Color1 = color1;
        Interval = interval;
        Level = level;
    }

    void wasteStaticUpdate()
    {
       setBrightness(MAX_BRIGHTNESS);
      for(int i=0; i<Level; i++)
        {
            setPixelColor(i, Color1);
        }
        show();
        //Increment();
    }

    /****** WASTE ******/
   void waste(uint32_t color1, uint8_t interval, uint8_t level, uint8_t index)
    {
        ActivePattern = WASTE;
        TotalSteps = 255;
        Index = index;
        Color1 = color1;
        Interval = 0;
        Level = level;
    }

    void wasteUpdate()
    {

      if(Index == OFFSET_WASTE){
        turnOff();
        setBrightness(MAX_BRIGHTNESS);
      }

      
      setPixelColor(Index, Color1);
      show();
     if(Index < Level){
           Index++;
      }
      else{
       if (OnComplete != NULL)
                {
                    OnComplete(); // call the comlpetion callback
                }
      }
}
    

    /****** ARROW ANIMATION *****/
    void arrowAnimation(uint32_t color1, uint8_t interval)
    {
        ActivePattern = ARROW;
        TotalSteps = LEG_ARROW;
        Index = 0;
        Jindex = 0;
        Color1 = color1;
        Interval = interval;
        Prev = millis();
        
    }

    void arrowAnimationUpdate()
    {
       
       setBrightness(MAX_BRIGHTNESS);

      
      if(millis() - Prev > Interval){
        Serial.println("go");
        Serial.println(First_half);
        Serial.println(Index);
        Serial.println(Jindex);
        Prev = millis();
       
        if(Index < 0){
          Increment();
          First_half = false;
          Jindex = 0;
          
        }
        if(Index == 0 && Jindex == 0 && !First_half){
          turnOff();
          Serial.println("Start");
        }
      if(!First_half){
          if(Jindex < LEG_ARROW - Index){
            setPixelColor(arrowLeg[Jindex-1], Color(0, 0, 0)); // turn previous LED off
            setPixelColor(arrowLeg[Jindex], Color(0, 255, 0)); // turn current LED on
            show(); 
            Jindex++;
          }
          else{
          
            Increment();
            Jindex = 0;
          }
      }
      
      if(Index == LEG_ARROW-1 && not First_half){
        Serial.println("first half done");
        First_half = true;
        Index = 0;
        Jindex = 0;
      }

      if(First_half){
        
        setPixelColor(arrowBranch1[Index], Color(0, 255, 0));
        setPixelColor(arrowBranch2[Index], Color(0, 255, 0));
        show();
        Increment();
        
        if(Index == LEG_ARROW-1){
          Serial.println("finish second half");
          First_half = false;
          Index = -1;
          
        }
      }
      
      }
    }
    
    /****** ARROW ******/
   void arrow(uint32_t color1, uint8_t interval)
    {
        ActivePattern = ARROW;
        TotalSteps = 255;
        Index = 0;
        Color1 = color1;
        Interval = interval;
    }

    void arrowUpdate()
    {
      setBrightness(MAX_BRIGHTNESS);
      for(int i=0; i< MAX_ARROW; i++)
        {
            setPixelColor(arrow_indices[i], Color1);
        }
        show();
    }

    /****** CROSS ******/
   void cross(uint32_t color1, uint8_t interval)
    {
        ActivePattern = CROSS;
        TotalSteps = 255;
        Index = 0;
        Color1 = color1;
        Interval = interval;
    }

    void crossUpdate()
    {
      setBrightness(MAX_BRIGHTNESS);
      for(int i=0; i< MAX_CROSS; i++)
        {
            setPixelColor(cross_indices[i], Color1);
        }
        show();
    }

    /****** BREATHE ******/
    void breathe(uint32_t color1, uint8_t interval, direction dir = FORWARD)
    {
        ActivePattern = BREATHE;
        TotalSteps = 255;
        Index = 0;
        Color1 = color1;
        Direction = dir;
        Intensity = 0;
        IntensityOld = 0;
        Interval = interval;

    }

    void breatheUpdate()
    {
     Intensity = MAX_BRIGHTNESS/2 * (1-cos(SPEED_FACTOR * Index));
     BrigthSet(Color1, Intensity);
     IncrementBreathe();
  
    }

   void BrigthSet(uint32_t color, float b)
   {
        setBrightness(b);
        for (int i = 0; i < numPixels(); i++)
        {
            setPixelColor(i, color);
        }
        show();
   }

    void turnOff()
    {
      Serial.println("turn off");
      for (int i = 0; i < numPixels(); ++i)
      { 
      setPixelColor(i, Color(0,0,0)); 
  
      }
     show();
    }

};

void Ring1Complete();
void StickComplete();
void MatrixComplete();
void UnsortedComplete();
 

NeoPatterns Ring1(RING_PIXELS, PIN_RING, NEO_GRB + NEO_KHZ800, &Ring1Complete);
NeoPatterns Stick(CAMERA_PIXELS, PIN_CAMERA,  NEO_GRBW + NEO_KHZ800, &StickComplete);
NeoPatterns Matrix(MATRIX_PIXELS, PIN_MATRIX,  NEO_GRB + NEO_KHZ800, &MatrixComplete);
NeoPatterns UnsortedRing(WASTE_RING_PIXELS, PIN_UNSORTED, NEO_GRBW + NEO_KHZ800, &UnsortedComplete);
NeoPatterns UnsortedFull(WASTE_FULL_PIXELS, PIN_UNSORTED, NEO_GRB + NEO_KHZ800, &UnsortedComplete);
NeoPatterns PlasticRing(WASTE_RING_PIXELS, PIN_PLASTIC, NEO_GRBW + NEO_KHZ800, &UnsortedComplete);
NeoPatterns PlasticFull(WASTE_FULL_PIXELS, PIN_PLASTIC, NEO_GRB + NEO_KHZ800, &UnsortedComplete);
NeoPatterns PaperRing(WASTE_RING_PIXELS, PIN_PAPER, NEO_GRBW + NEO_KHZ800, &UnsortedComplete);
NeoPatterns PaperFull(WASTE_FULL_PIXELS, PIN_PAPER, NEO_GRB + NEO_KHZ800, &UnsortedComplete);
NeoPatterns GlassRing(WASTE_RING_PIXELS, PIN_GLASS, NEO_GRBW + NEO_KHZ800, &UnsortedComplete);
NeoPatterns GlassFull(WASTE_FULL_PIXELS, PIN_GLASS, NEO_GRB + NEO_KHZ800, &UnsortedComplete);


int msg;
int msgLength;
char payload[10];
char msgType;
bool inMsg = false;
bool endOfMsg = false;

void setup()
{
  Serial.begin(115200);
 
    
    // Initialize all the pixelStrips
    Ring1.begin();
    Stick.begin();
    Matrix.begin();
    UnsortedRing.begin();
    UnsortedFull.begin();
    PlasticRing.begin();
    PlasticFull.begin();
    PaperRing.begin();
    PaperFull.begin();
    GlassRing.begin();
    GlassFull.begin();
    
    // Kick off a pattern
    Ring1.onStatic(Ring1.Color(0,255,0), 0);
    Stick.onStatic(Stick.Color(255,0,0), 0);
    Matrix.arrow(Stick.Color(0,255,0), 0);
    UnsortedRing.onStatic(UnsortedRing.Color(255,255,255,255), 0);
    UnsortedFull.onStatic(UnsortedFull.Color(255, 0, 0), 0);
    PlasticRing.onStatic(PlasticRing.Color(255,255,255,255), 0);
    PlasticFull.onStatic(PlasticFull.Color(255, 0, 0), 0);
    PaperRing.onStatic(PaperRing.Color(255,255,255,255), 0);
    PaperFull.onStatic(PaperFull.Color(255, 0, 0), 0);
    GlassRing.onStatic(GlassRing.Color(255,255,255,255), 0);
    GlassFull.onStatic(GlassFull.Color(255, 0, 0), 0);
    Ring1.Update();
    Stick.Update();
    Matrix.Update();
    UnsortedFull.Update();
    UnsortedRing.Update();
    PlasticRing.Update();
    PlasticFull.Update();
    PaperRing.Update();
    PaperFull.Update();
    GlassRing.Update();
    GlassFull.Update();
    delay(1000);

    Ring1.Color1 = Ring1.Color(255,0,0);
    Stick.Color1 = Stick.Color(0,0,255);
    Matrix.ActivePattern = CROSS;
    Matrix.Color1 = Stick.Color(255,0,0);
    UnsortedRing.onStatic(UnsortedRing.Color(255,0,0,0), 0);
    UnsortedFull.onStatic(UnsortedFull.Color(255, 0, 0), 0);
    PlasticRing.onStatic(UnsortedRing.Color(255,0,0,0), 0);
    PlasticFull.onStatic(UnsortedFull.Color(255, 0, 0), 0);
    PaperRing.onStatic(PaperRing.Color(255,0,0,0), 0);
    PaperFull.onStatic(PaperFull.Color(255, 0, 0), 0);
    GlassRing.onStatic(GlassRing.Color(255,0,0,0), 0);
    GlassFull.onStatic(GlassFull.Color(255, 0, 0), 0);
    Ring1.Update();
    Stick.Update();    
    Matrix.Update();
    UnsortedRing.Update();
    UnsortedFull.Update();
    PlasticRing.Update();
    PlasticFull.Update();
    PaperRing.Update();
    PaperFull.Update();
    GlassRing.Update();
    GlassFull.Update();
    delay(1000);
  
    Ring1.Color1 = Ring1.Color(0,0,0);
    Stick.Color1 = Stick.Color(0,0,0);
    Matrix.ActivePattern = STATIC;
    Matrix.Color1 = Matrix.Color(0,0,0);
    UnsortedRing.onStatic(UnsortedRing.Color(0,0,0,0), 0);
    UnsortedFull.onStatic(UnsortedFull.Color(0, 0, 0), 0);  
    PlasticRing.onStatic(UnsortedRing.Color(0,0,0,0), 0);
    PlasticFull.onStatic(UnsortedFull.Color(0, 0, 0), 0);
    PaperRing.onStatic(PaperRing.Color(0,0,0,0), 0);
    PaperFull.onStatic(PaperFull.Color(0, 0, 0), 0);
    GlassRing.onStatic(GlassRing.Color(0,0,0,0), 0);
    GlassFull.onStatic(GlassFull.Color(0, 0, 0), 0);
    
}


void loop()
{
    Ring1.Update();
    Stick.Update();
    Matrix.Update();
    UnsortedRing.Update();
    UnsortedFull.Update();
    PlasticRing.Update();
    PlasticFull.Update();
    PaperRing.Update();
    PaperFull.Update();
    GlassRing.Update();
    GlassFull.Update();

if (Serial.available()>0) {
    msg=Serial.read();
    Serial.println(msg);
    
    if(msg == 35){
      inMsg = true;
      msgLength = -1;
   
    }else{
    
      if(msg == 33){
        inMsg = false;
        endOfMsg = true;
      }

      if(inMsg){
        if(msgLength < 0){
          msgType = (char)msg;
        
        }else{
          payload[msgLength] = (char)msg;
          
        }
        msgLength++;
      }
    }

    if(endOfMsg){
      payload[msgLength] = '\0';
      endOfMsg = false;
      switchData(payload);
      
    }
  }
    
}


void switchData(char p[]){
  
  int n = atoi(p);
  //Serial.println(msgType);
  switch(msgType){
    case 'P':
      Serial.print("Plastic to ");
      PlasticRing.Index = 3;
      if(n < 100){
        PlasticRing.ActivePattern = WASTE;
        PlasticRing.Color1 = PlasticRing.Color(255,255,255,220);
        PlasticRing.Interval = WASTE_RING_SPEED;
      }
      if(n == 100){
        PlasticRing.ActivePattern = WASTE;
        PlasticRing.Color1 = PlasticRing.Color(0,220,10,1);
        PlasticRing.Interval = WASTE_RING_SPEED;
      }

      if(n == 333){
        //n = 100;
        PlasticRing.ActivePattern = STATIC;
        PlasticRing.Color1 = PlasticRing.Color(255,255,255,220);
        //UnsortedRing.Interval = 1;
      }

      PlasticRing.Level = map(n, 0, 100, OFFSET_WASTE, WASTE_RING_PIXELS-OFFSET_WASTE-1);
      break;
    case 'U':
      Serial.print("Unsorted to ");

      UnsortedRing.Index = 3;
      if(n < 100){
        UnsortedRing.ActivePattern = WASTE;
        UnsortedRing.Color1 = UnsortedRing.Color(255,255,255,220);
        UnsortedRing.Interval = WASTE_RING_SPEED;
      }
      if(n == 100){
        UnsortedRing.ActivePattern = WASTE;
        UnsortedRing.Color1 = UnsortedRing.Color(255,0,0,0);
        UnsortedRing.Interval = WASTE_RING_SPEED;
      }

      if(n == 333){
        //n = 100;
        UnsortedRing.ActivePattern = STATIC;
        UnsortedRing.Color1 = UnsortedRing.Color(255,255,255,220);
        //UnsortedRing.Interval = 1;
      }

      UnsortedRing.Level = map(n, 0, 100, OFFSET_WASTE, WASTE_RING_PIXELS-OFFSET_WASTE-1);
      break;
    case 'C':
      Serial.print("Paper (C) to ");
      PaperRing.Index = 3;
      if(n < 100){
        PaperRing.ActivePattern = WASTE;
        PaperRing.Color1 = PaperRing.Color(255,255,255,220);
        PaperRing.Interval = WASTE_RING_SPEED;
      }
      if(n == 100){
        PaperRing.ActivePattern = WASTE;
        PaperRing.Color1 = PaperRing.Color(255,0,0,0);
        PaperRing.Interval = WASTE_RING_SPEED;
      }

      if(n == 333){
        //n = 100;
        PaperRing.ActivePattern = STATIC;
        PaperRing.Color1 = PaperRing.Color(255,255,255,220);
        //UnsortedRing.Interval = 1;
      }

      PaperRing.Level = map(n, 0, 100, OFFSET_WASTE, WASTE_RING_PIXELS-OFFSET_WASTE-1);
      break;
    case 'G':
      Serial.print("Glass to ");

      GlassRing.Index = 3;
      if(n < 100){
        GlassRing.ActivePattern = WASTE;
        GlassRing.Color1 = GlassRing.Color(255,255,255,220);
        GlassRing.Interval = WASTE_RING_SPEED;
      }
      if(n == 100){
        GlassRing.ActivePattern = WASTE;
        GlassRing.Color1 = GlassRing.Color(255,0,0,0);
        GlassRing.Interval = WASTE_RING_SPEED;
      }

      if(n == 333){
        //n = 100;
        GlassRing.ActivePattern = STATIC;
        GlassRing.Color1 = GlassRing.Color(255,255,255,220);
        //UnsortedRing.Interval = 1;
      }

      GlassRing.Level = map(n, 0, 100, OFFSET_WASTE, WASTE_RING_PIXELS-OFFSET_WASTE-1);
      break;
    case 'D':
      Serial.print("Door to ");
      Serial.println(n);
      switchDoor(n);
      break;
    case 'R':
      Serial.print("Ring to ");
      Serial.println(n);
      switchRing(n);
      break;
    case 'M':
      Serial.print("Matrix to ");
      Serial.println(n);
      switchMatrix(n);
      break;
     
  }
}



void switchMatrix(int my_type){
  switch(my_type){
    case 0:
      //off
      Matrix.ActivePattern = STATIC;
      Matrix.Color1 = Matrix.Color(0,0,0);
      break;
      
    case 1:
      //green arrow 
      Matrix.ActivePattern = ARROW;
      Matrix.Color1 = Matrix.Color(0,255,0);
      break;
      
    case 2:
      //red cross
      Matrix.ActivePattern = CROSS;
      Matrix.Color1 = Matrix.Color(255,0,0);
      break;
      
    case 3:
      //green animation
      Matrix.ActivePattern = ARROW_ANIMATION;
      Matrix.Color1 = Matrix.Color(0,255,0);
      Matrix.Interval = 100;
      break;
    
    default:      
      //off
      Matrix.ActivePattern = STATIC;
      Matrix.Color1 = Matrix.Color(0,0,0);
      break;
  }
}


void switchRing(int my_type){
  switch(my_type){
    case 0:
      //off
      Ring1.ActivePattern = STATIC;
      Ring1.Color1 = Ring1.Color(0,0,0);
      break;
      
    case 1:
      //green 
      Ring1.ActivePattern = STATIC;
      Ring1.Color1 = Ring1.Color(0,255,0);
      break;
      
    case 2:
      //red
      Ring1.ActivePattern = STATIC;
      Ring1.Color1 = Ring1.Color(255,0,0);
      break;
      
    case 3:
      //green breathe
      Ring1.ActivePattern = BREATHE;
      Ring1.Color1 = Ring1.Color(0,255,0);
      break;
      
    case 4:
      //red breathe
      Ring1.ActivePattern = BREATHE;
      Ring1.Color1 = Ring1.Color(255,0,0);
      break;

    default:
      Ring1.ActivePattern = STATIC;
      Ring1.Color1 = Ring1.Color(0,0,0);
      break;
  }
}

void switchDoor(int my_type){
  Serial.println(my_type);
  switch(my_type){
    case 0:
      //off
      Stick.ActivePattern = STATIC;
      Stick.Color1 = Stick.Color(0,0,0);
      break;
    case 1:
      //white on
      Stick.ActivePattern = STATIC;
      Stick.Color1 = Stick.Color(255,255,255);
      break;
    case 2:
      //breathe white
      Stick.ActivePattern = BREATHE;
      Stick.Color1 = Stick.Color(255,2552,255);
      break;

    default:
      //off
      Stick.ActivePattern = STATIC;
      Stick.Color1 = Stick.Color(0,0,0);
      break;
  }
}




void Ring1Complete()
{
  Serial.println("ring complete");
  Ring1.Reverse();
}

void StickComplete()
{
  Serial.println("Stick complete");
  Stick.Reverse();
}

void MatrixComplete()
{
  Serial.println("Matrix complete");
}

void UnsortedComplete(){
  UnsortedRing.ActivePattern = MY_STATIC;
  
  Serial.println("Unsorted complete");
}

