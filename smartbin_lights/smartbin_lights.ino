#include <Adafruit_NeoPixel.h>

/****** NEOPIXEL ******/
#define PIN            6
#define NUMPIXELS      24

Adafruit_NeoPixel led_door = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

int msg;
int msgLength;
char payload[10];
char msgType;
bool inMsg = false;
bool endOfMsg = false;

void setup()
{
  Serial.begin(115200);
  delay(1000);
  Serial.println("Sto avviando...");

  led_door.begin();
  led_door.setBrightness(10);
  testNeoPixel();
}


void loop()
{
  
  if (Serial.available()>0) {
    msg=Serial.read();
    //Serial.println(msg);
    
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
  Serial.println(msgType);
  switch(msgType){
    case 'P':
      Serial.println("Plastic to ");
      Serial.println(n);
      break;
    case 'U':
      Serial.println("Unsorted to ");
      Serial.println(n);
      break;
    case 'C':
      Serial.println("Paper (C) to ");
      Serial.println(n);
      break;
    case 'G':
      Serial.println("Glass to ");
      Serial.println(n);
      break;
    case 'D':
      Serial.println("Door to ");
      Serial.println(n);
      switchDoor(n);
      break;
    case 'R':
      Serial.println("Ring to ");
      Serial.println(n);
      break;
    case 'S':
      Serial.println("Sportello to ");
      Serial.println(n);
      break;
     
  }
}

void switchDoor(char my_type){
  Serial.println("type : ");
  Serial.print(my_type);
  switch(my_type){
    case 0:
      offCameraLight();
      break;
    case 1:
      onCameraLight();
      break;
    case 2:
      blinkCameraLight();
      break;
  }
}
void onCameraLight(){
  //Serial.println("turn on the door led");
  for(int i=0;i<NUMPIXELS;i++){
      led_door.setPixelColor(i, led_door.Color(255,255,255)); 
   }
   led_door.show(); 
}

void offCameraLight(){
  //Serial.println("turn off the door led");
  for(int i=0;i<NUMPIXELS;i++){
      led_door.setPixelColor(i, led_door.Color(0,0,0)); 
   }
   led_door.show(); 
}

void blinkCameraLight(){
  
  /*
  onCameraLight();
  delay(500);
  offCameraLight();
  delay(500);
  */
  float frequency = 0.008;
  float maximumBrightness = 255;
  
  for (int i = 0; i < 2000; i++) {
    Serial.println(frequency*i);
    float intensity = maximumBrightness/2.0 * (1.0 + sin(frequency * i));
    if(intensity == 10){
       Serial.println("-------------_");
      Serial.println(i);
      delay(10);
     
    }
    led_door.setBrightness(intensity);
    for (int ledNumber=0; ledNumber<NUMPIXELS; ledNumber++) {
      led_door.setPixelColor(ledNumber, 0, 0, 255);
    }

    led_door.show();
  }
}


void testNeoPixel(){
  Serial.println("Neo Pixel test");
  for(int i=0;i<NUMPIXELS;i++){
      led_door.setPixelColor(i, led_door.Color(255,255,255)); 
   }
   led_door.show(); 
   delay(500);
   for(int i=0;i<NUMPIXELS;i++){
      led_door.setPixelColor(i, led_door.Color(255,0,0)); 
   }
   led_door.show(); 
   delay(500);
   for(int i=0;i<NUMPIXELS;i++){
      led_door.setPixelColor(i, led_door.Color(0,0,0)); 
   }
   led_door.show(); 
}
