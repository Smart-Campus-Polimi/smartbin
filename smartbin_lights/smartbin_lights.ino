#include <Adafruit_NeoPixel.h>

/****** NEOPIXEL ******/
#define PIN            6
#define NUMPIXELS      24

Adafruit_NeoPixel led_door = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

int door_status = 0;

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
  Serial.println(door_status);
  if (Serial.available()>0) {
    door_status=Serial.read();
    
    switch(door_status){
      case 65:
          offCameraLight();
          break;

      case 66:
          onCameraLight();
          break;

      case 67:
          blinkCameraLight();
          break;
          
      default:
          offCameraLight();
          break;
    }
    
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
  onCameraLight();
  delay(500);
  offCameraLight();
  delay(500);
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
