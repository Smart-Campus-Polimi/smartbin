#include <Adafruit_NeoPixel.h>

#define MAX_BRIGHTNESS      90
#define SPEED_FACTOR          0.08
#define WASTE_RING_SPEED     20
/****** NEOPIXEL CAMERA ******/
#define PIN_CAMERA            6
#define CAMERA_PIXELS        48
/****** NEOPIXEL RING ******/
#define PIN_RING              7
#define RING_PIXELS         162

/****** WASTE RING ******/
#define PIN_UNSORTED          2
#define PIN_PLASTIC           5
#define PIN_PAPER             4
#define PIN_GLASS             3

#define WASTE_RING_PIXELS    60
#define OFFSET_WASTE          4

/****** MATRIX ******/
#define PIN_MATRIX            0
#define MATRIX_PIXELS        64
/***** ARROW ANIMATION *****/
#define LEG_ARROW             8
#define BRANCH_ARROW          5
#define MAX_ARROW            18
#define MAX_CROSS            13

const int arrow_indices[MAX_ARROW] = {0, 9, 18, 27, 36, 45, 54, 63, 1, 2, 3, 4, 5, 8, 16, 24, 32, 40};
const int cross_indices[MAX_CROSS] = {12, 20, 28, 33, 34, 35, 36, 37, 38, 39, 44, 52, 60};

const int arrowLeg[LEG_ARROW] = {0, 9, 18, 27, 36, 45, 54, 63};
const int arrowBranch1[BRANCH_ARROW] = {8, 16, 24, 32, 40};
const int arrowBranch2[BRANCH_ARROW] = {1, 2, 3, 4,5};




enum  pattern { NONE, STATIC, BLINK, BREATHE, ARROW_ANIMATION, ARROW, CROSS, WASTE, MY_STATIC};
enum  direction { FORWARD, REVERSE };

class NeoPatterns : public Adafruit_NeoPixel
{
  public:

    pattern ActivePattern;
    direction Direction;
    unsigned long Interval;
    unsigned long lastUpdate = 0;

    uint32_t Color1;
    uint16_t TotalSteps;
    uint16_t Index;
    uint16_t Jindex;
    uint16_t Prev;
    uint8_t Level;



    float Intensity, IntensityOld;
    bool First_half = false;

    void (*OnComplete)();  // Callback on completion of pattern

    NeoPatterns(uint16_t pixels, uint8_t pin, uint8_t type, void (*callback)())
      : Adafruit_NeoPixel(pixels, pin, type)
    {
      OnComplete = callback;
    }

    void Update()
    {
      if ((millis() - lastUpdate) > Interval) // time to update
      {
        lastUpdate = millis();
        switch (ActivePattern)
        {
          case NONE:
            break;
          case STATIC:
            onStaticUpdate();
            break;
          case BLINK:
            break;
          case BREATHE:
            breatheUpdate();
            break;
          case ARROW_ANIMATION:
            //turnOff();
            arrowAnimationUpdate();
            break;
          case ARROW:
            //turnOff();
            arrowUpdate();
            break;
          case CROSS:
            //turnOff();
            crossUpdate();
            break;
          case WASTE:
            wasteUpdate();
            break;
          default:
            break;
        }
      }
    }


    void IncrementBreathe() {
      IntensityOld = Intensity;
      if (Direction == FORWARD)
      {
        Index++;
        if (Intensity < IntensityOld)
        {
          if (OnComplete != NULL)
          {
            OnComplete();
          }
        }
      }
      else // Direction == REVERSE
      {
        --Index;
        if (Intensity > IntensityOld)
        {
          if (OnComplete != NULL)
          {
            OnComplete();
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

    
    void Reverse()
    {
      if (Direction == FORWARD)
      {
        Direction = REVERSE;
        Index = TotalSteps - 1;
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
      Index = 0;
      TotalSteps = 255;
      Color1 = color1;
      Interval = interval;
    }

    void onStaticUpdate()
    {
      setBrightness(MAX_BRIGHTNESS);
      for (int i = 0; i < numPixels(); i++)
      {
        setPixelColor(i, Color1);
      }
      show();
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


      
        Serial.println("go");
        Serial.println(First_half);
        Serial.println(Index);
        Serial.println(Jindex);
        Prev = millis();

        if (Index < 0) {
          Increment();
          First_half = false;
          Jindex = 0;

        }
        if (Index == 0 && Jindex == 0 && !First_half) {
          turnOff();
          Serial.println("Start");
        }
        if (!First_half) {
          if (Jindex < LEG_ARROW - Index) {
            setPixelColor(arrowLeg[Jindex - 1], Color(0, 0, 0)); // turn previous LED off
            setPixelColor(arrowLeg[Jindex], Color(0, 255, 0)); // turn current LED on
            show();
            Jindex++;
          }
          else {

            Increment();
            Jindex = 0;
          }
        }

        if (Index == LEG_ARROW - 1 && not First_half) {
          Serial.println("first half done");
          First_half = true;
          Index = 0;
          Jindex = 0;
        }

        if (First_half) {

          setPixelColor(arrowBranch1[Index], Color(0, 255, 0));
          setPixelColor(arrowBranch2[Index], Color(0, 255, 0));
          show();
          Increment();

          if (Index == LEG_ARROW - 1) {
            Serial.println("finish second half");
            First_half = false;
            Index = -1;

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
      for (int i = 0; i < MAX_ARROW; i++)
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
      for (int i = 0; i < MAX_CROSS; i++)
      {
        setPixelColor(cross_indices[i], Color1);
      }
      show();
    }

    /****** WASTE ******/
    void waste(uint32_t color1, int level)
    {
      ActivePattern = WASTE;
      Index = 0;
      Color1 = color1;
      Interval = 0;
      Level = level;
    }

    void wasteUpdate()
    {
      Serial.println(Index);
      if (Index == 101) {
        turnOff();
        setBrightness(MAX_BRIGHTNESS);
        if (Level == WASTE_RING_PIXELS) {
          Index = 0;
        } else {
          Index = OFFSET_WASTE;
        }
      }


      setPixelColor(Index, Color1);
      show();


      if (Index < Level) {
        Index++;
      }
    }





    /****** BREATHE ******/
    void breathe(uint32_t color1, uint8_t interval, direction dir = FORWARD)
    {
      ActivePattern = BREATHE;
      Index = 0;
      Color1 = color1;
      Direction = dir;
      Intensity = 0;
      IntensityOld = 0;
      Interval = interval;
      TotalSteps = 255;

    }

    void breatheUpdate()
    {
      Intensity = MAX_BRIGHTNESS  * (1 - cos(SPEED_FACTOR * Index));
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
        setPixelColor(i, Color(0, 0, 0));

      }
      show();
    }

};

void BigRingComplete();
void StickComplete();
void MatrixComplete();
void UnsortedComplete();


NeoPatterns BigRing(RING_PIXELS, PIN_RING, NEO_GRB + NEO_KHZ800, &BigRingComplete);
NeoPatterns Stick(CAMERA_PIXELS, PIN_CAMERA,  NEO_GRBW + NEO_KHZ800, &StickComplete);
NeoPatterns Matrix(MATRIX_PIXELS, PIN_MATRIX,  NEO_GRB + NEO_KHZ800, &MatrixComplete);
NeoPatterns UnsortedRing(WASTE_RING_PIXELS, PIN_UNSORTED, NEO_GRBW + NEO_KHZ800, &UnsortedComplete);
NeoPatterns PlasticRing(WASTE_RING_PIXELS, PIN_PLASTIC, NEO_GRBW + NEO_KHZ800, &UnsortedComplete);
NeoPatterns PaperRing(WASTE_RING_PIXELS, PIN_PAPER, NEO_GRBW + NEO_KHZ800, &UnsortedComplete);
NeoPatterns GlassRing(WASTE_RING_PIXELS, PIN_GLASS, NEO_GRBW + NEO_KHZ800, &UnsortedComplete);


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
  BigRing.begin();
  Stick.begin();
  Matrix.begin();
  UnsortedRing.begin();
  PlasticRing.begin();
  PaperRing.begin();
  GlassRing.begin();

  // Kick off a pattern
  BigRing.onStatic(BigRing.Color(0, 255, 0), 0);
  Stick.onStatic(Stick.Color(255, 0, 0), 0);
  Matrix.arrow(Stick.Color(0,255,0), 0);
  UnsortedRing.onStatic(UnsortedRing.Color(255, 255, 255, 255), 0);
  PlasticRing.onStatic(PlasticRing.Color(255, 255, 255, 255), 0);
  PaperRing.onStatic(PaperRing.Color(255, 255, 255, 255), 0);
  GlassRing.onStatic(GlassRing.Color(255, 255, 255, 255), 0);
  BigRing.Update();
  Stick.Update();
  Matrix.Update();
  UnsortedRing.Update();
  PlasticRing.Update();
  PaperRing.Update();
  GlassRing.Update();
  delay(1000);

  BigRing.Color1 = BigRing.Color(255, 0, 0);
  Stick.Color1 = Stick.Color(0, 0, 255);
  Matrix.ActivePattern = CROSS;
    Matrix.Color1 = Stick.Color(255,0,0);
  UnsortedRing.Color1 = UnsortedRing.Color(255, 0, 0, 0);
  PlasticRing.Color1 = PlasticRing.Color(255, 0, 0, 0);
  PaperRing.Color1 = PaperRing.Color(255, 0, 0, 0);
  GlassRing.Color1 = GlassRing.Color(255, 0, 0, 0);
  BigRing.Update();
  Stick.Update();
  Matrix.Update();
  UnsortedRing.Update();
  PlasticRing.Update();
  PaperRing.Update();
  GlassRing.Update();
  delay(1000);

  BigRing.Color1 = BigRing.Color(0, 0, 0);
  Stick.Color1 = Stick.Color(0, 0, 0);
  Matrix.ActivePattern = STATIC;
  Matrix.Color1 = Matrix.Color(0,0,0);
  UnsortedRing.Color1 = UnsortedRing.Color(0, 0, 0, 0);
  PlasticRing.Color1 = PlasticRing.Color(0, 0, 0, 0);
  PaperRing.Color1 = PaperRing.Color(0, 0, 0, 0);
  GlassRing.Color1 = GlassRing.Color(0, 0, 0, 0);

}


void loop()
{
  BigRing.Update();
  Stick.Update();
  Matrix.Update();
  UnsortedRing.Update();
  PlasticRing.Update();
  PaperRing.Update();
  GlassRing.Update();

  if (Serial.available() > 0) {
    msg = Serial.read();
    Serial.println(msg);

    if (msg == 35) {
      inMsg = true;
      msgLength = -1;

    } else {

      if (msg == 33) {
        inMsg = false;
        endOfMsg = true;
      }

      if (inMsg) {
        if (msgLength < 0) {
          msgType = (char)msg;

        } else {
          payload[msgLength] = (char)msg;

        }
        msgLength++;
      }
    }

    if (endOfMsg) {
      payload[msgLength] = '\0';
      endOfMsg = false;
      switchData(payload);

    }
  }

}


void switchData(char p[]) {

  int n = atoi(p);
  //Serial.println(msgType);
  switch (msgType) {
    case 'P':
      Serial.print("Plastic to ");
      PlasticRing.ActivePattern = WASTE;
      PlasticRing.Index = 101;
      if (n==0){
         PlasticRing.Color1 = PlasticRing.Color(0, 0, 0, 0);
      }
      
      if (n > 0 && n < 100) {
        PlasticRing.Color1 = PlasticRing.Color(255, 255, 255, 220);
        PlasticRing.Interval = WASTE_RING_SPEED;
        PlasticRing.Level = map(n, 0, 100, OFFSET_WASTE, WASTE_RING_PIXELS - OFFSET_WASTE - 1);
      }
      if (n == 100) {
        PlasticRing.Color1 = PlasticRing.Color(255, 0, 0, 0);
        PlasticRing.Interval = WASTE_RING_SPEED / 2;
        PlasticRing.Level = WASTE_RING_PIXELS;
      }

      if (n == 333) {
        PlasticRing.Color1 = PlasticRing.Color(255, 255, 255, 220);
        PlasticRing.Interval = 0;
        PlasticRing.Level = map(100, 0, 100, OFFSET_WASTE, WASTE_RING_PIXELS - OFFSET_WASTE - 1);
      }

      break;
    case 'U':
      Serial.print("Unsorted to ");

      UnsortedRing.ActivePattern = WASTE;
      UnsortedRing.Index = 101;

      if (n==0){
         UnsortedRing.Color1 = UnsortedRing.Color(0, 0, 0, 0);
      }
      
      if (n > 0 && n < 100) {
        UnsortedRing.Color1 = UnsortedRing.Color(255, 255, 255, 220);
        UnsortedRing.Interval = WASTE_RING_SPEED;
        UnsortedRing.Level = map(n, 0, 100, OFFSET_WASTE, WASTE_RING_PIXELS - OFFSET_WASTE - 1);
      }
      if (n == 100) {
        UnsortedRing.Color1 = UnsortedRing.Color(255, 0, 0, 0);
        UnsortedRing.Interval = WASTE_RING_SPEED / 2;
        UnsortedRing.Level = WASTE_RING_PIXELS;
      }

      if (n == 333) {
        UnsortedRing.Color1 = UnsortedRing.Color(255, 255, 255, 220);
        UnsortedRing.Interval = 0;
        UnsortedRing.Level = map(100, 0, 100, OFFSET_WASTE, WASTE_RING_PIXELS - OFFSET_WASTE - 1);
      }
      break;
    case 'C':
      Serial.print("Paper (C) to ");
      PaperRing.ActivePattern = WASTE;
      PaperRing.Index = 101;

      if (n==0){
         PaperRing.Color1 = PaperRing.Color(0, 0, 0, 0);
      }
      
      if (n > 0 && n < 100) {
        PaperRing.Color1 = PaperRing.Color(255, 255, 255, 220);
        PaperRing.Interval = WASTE_RING_SPEED;
        PaperRing.Level = map(n, 0, 100, OFFSET_WASTE, WASTE_RING_PIXELS - OFFSET_WASTE - 1);
      }
      if (n == 100) {
        PaperRing.Color1 = PlasticRing.Color(255, 0, 0, 0);
        PaperRing.Interval = WASTE_RING_SPEED / 2;
        PaperRing.Level = WASTE_RING_PIXELS;
      }

      if (n == 333) {
        PaperRing.Color1 = PaperRing.Color(255, 255, 255, 220);
        PaperRing.Interval = 0;
        PaperRing.Level = map(100, 0, 100, OFFSET_WASTE, WASTE_RING_PIXELS - OFFSET_WASTE - 1);
      }
      break;
    case 'G':
      Serial.print("Glass to ");
      GlassRing.ActivePattern = WASTE;
      GlassRing.Index = 101;

      if (n==0){
         GlassRing.Color1 = GlassRing.Color(0, 0, 0, 0);
      }
      
      if (n > 0 && n < 100) {
        GlassRing.Color1 = GlassRing.Color(255, 255, 255, 220);
        GlassRing.Interval = WASTE_RING_SPEED;
        GlassRing.Level = map(n, 0, 100, OFFSET_WASTE, WASTE_RING_PIXELS - OFFSET_WASTE - 1);
      }
      if (n == 100) {
        GlassRing.Color1 = GlassRing.Color(255, 0, 0, 0);
        GlassRing.Interval = WASTE_RING_SPEED / 2;
        GlassRing.Level = WASTE_RING_PIXELS;
      }

      if (n == 333) {
        GlassRing.Color1 = GlassRing.Color(255, 255, 255, 220);
        GlassRing.Interval = 0;
        GlassRing.Level = map(100, 0, 100, OFFSET_WASTE, WASTE_RING_PIXELS - OFFSET_WASTE - 1);
      }
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

void switchRing(int my_type) {
  switch (my_type) {
    case 0:
      //off
      BigRing.ActivePattern = STATIC;
      BigRing.Color1 = BigRing.Color(0, 0, 0);
      break;

    case 1:
      //green
      BigRing.ActivePattern = STATIC;
      BigRing.Color1 = BigRing.Color(0, 255, 0);
      break;

    case 2:
      //red
      BigRing.ActivePattern = STATIC;
      BigRing.Color1 = BigRing.Color(255, 0, 0);
      break;

    case 3:
      //green breathe
      BigRing.ActivePattern = BREATHE;
      BigRing.Color1 = BigRing.Color(0, 255, 0);
      break;

    case 4:
      //red breathe
      BigRing.ActivePattern = BREATHE;
      BigRing.Color1 = BigRing.Color(255, 0, 0);
      break;

    default:
      BigRing.ActivePattern = STATIC;
      BigRing.Color1 = BigRing.Color(0, 0, 0);
      break;
  }
}

void switchDoor(int my_type) {
  Serial.println(my_type);
  switch (my_type) {
    case 0:
      //off
      Stick.ActivePattern = STATIC;
      Stick.Color1 = Stick.Color(0, 0, 0);
      break;
    case 1:
      //white on
      Stick.ActivePattern = STATIC;
      Stick.Color1 = Stick.Color(255, 255, 255);
      break;
    case 2:
      //breathe white
      Stick.ActivePattern = BREATHE;
      Stick.Color1 = Stick.Color(255, 2552, 255);
      break;

    default:
      //off
      Stick.ActivePattern = STATIC;
      Stick.Color1 = Stick.Color(0, 0, 0);
      break;
  }
}




void BigRingComplete()
{
  Serial.println("ring complete");
  BigRing.Reverse();
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

void UnsortedComplete() {
  //UnsortedRing.ActivePattern = MY_STATIC;

  Serial.println("Unsorted complete");
}

