// Arduino Wire library is required if I2Cdev I2CDEV_ARDUINO_WIRE implementation
// is used in I2Cdev.h
#include "Wire.h"

#include "I2Cdev.h"
#include "MPU6050.h"

#define LED_PIN 13
#define FLEX_PIN_1 0
#define FLEX_PIN_2 1
#define FLEX_PIN_3 2

#define FLEX_COUNT 3

MPU6050 accelgyro;

int16_t ax, ay, az;
int16_t gx, gy, gz;
char str[512];

bool blinkState = false;
int16_t ax_min, ay_min, az_min, ax_max, ay_max, az_max;

int16_t flexData[3];
int16_t flexDataMin[3];
int16_t flexDataMax[3];

void setup();
void loop();

void readFlexData(int* degrees1, int* degrees2, int* degrees3){
  int flex1, flex2, flex3;
  // read the voltage from the voltage divider (sensor plus resistor)
  flex1 = analogRead(FLEX_PIN_1);
  flex2 = analogRead(FLEX_PIN_2);
  flex3 = analogRead(FLEX_PIN_3);

  // convert the voltage reading to inches
  // the first two numbers are the sensor values for straight (510) and bent (610)
  // the second two numbers are the degree readings we'll map that to (0 to 90 degrees)
  *degrees1 = map(flex1, 510, 610, 0, 90);
  *degrees2 = map(flex2, 510, 610, 0, 90);
  *degrees3 = map(flex3, 510, 610, 0, 90);

  // print out the result
//  Serial.print("flex: {"); Serial.print(flex1,DEC);Serial.print(": "); Serial.print(*degrees1,DEC);Serial.print("} ");
//  Serial.print(flex2,DEC);Serial.print(": "); Serial.print(*degrees2,DEC);Serial.print("} ");
//  Serial.print(flex3,DEC);Serial.print(": "); Serial.print(*degrees3,DEC);Serial.println("} ");
}

/*
  SerialEvent occurs whenever a new data comes in the
 hardware serial RX.  This routine is run between each
 time loop() runs, so using delay inside loop can delay
 response.  Multiple bytes of data may be available.
 */
void serialEvent() {
  String serialDataIn;
  while (Serial.available()) {
    delay(3);  //delay to allow buffer to fill 
    if (Serial.available() >0) {
      char c = Serial.read();  //gets one byte from serial buffer
      serialDataIn += c; //makes the string readString
    } 
  }  
  
  if(serialDataIn.length() > 0){
    
    serialDataIn.replace("\n", "");
    if(serialDataIn.startsWith("min:") || serialDataIn.startsWith("max:")){
        char charBuf[serialDataIn.length()+1];
        serialDataIn.toCharArray(charBuf, serialDataIn.length()+1);
        if(serialDataIn.startsWith("min:")){
           
           sscanf(charBuf,"min:[%d, %d, %d, %d, %d, %d]\n",&ax_min, &ay_min,&az_min, &flexDataMin[0], &flexDataMin[1], &flexDataMin[2]);

//           Serial.print("**************min:");
//    Serial.print(ax_min);
//    Serial.print(flexDataMin[1]);
//    Serial.println(flexDataMin[2]);
//    Serial.flush();
        }else{
           sscanf(charBuf,"max:[%d, %d, %d, %d, %d, %d]\n",&ax_max, &ay_max,&az_max, &flexDataMax[0], &flexDataMax[1], &flexDataMax[2]);
 
// Serial.print("**************max:");
//          Serial.print(ax_max);
//    Serial.print(flexDataMax[1]);
//    Serial.println(flexDataMax[2]);
//    Serial.flush();
        }
        
        if(  (ax_min !=0 || ay_min!= 0 || az_min!=0) && (ax_max!=0 || ay_max!=0 || az_max!= 0)){
          Serial.println("?ok?");
        }
    Serial.flush();
    }
    
    
    
    
    
  }
}

void setup() {
  // join I2C bus (I2Cdev library doesn't do this automatically)
  Wire.begin();

  // initialize serial communication
  Serial.begin(9600);

  // initialize device
  Serial.println("Initializing I2C devices...");
  accelgyro.initialize();

  // verify connection
  Serial.println("Testing device connections...");
  Serial.println(accelgyro.testConnection() ? "MPU6050 connection successful" : "MPU6050 connection failed");

  // configure Arduino LED for
  pinMode(LED_PIN, OUTPUT);
  
  ax_min= ay_min= az_min= ax_max= ay_max= az_max= 0;
  for(int i=0; i< FLEX_COUNT; i++){
    flexDataMin[i] = flexDataMax[i] =0;
  }
  
}


void loop() {
  // read raw accel/gyro measurements from device
  accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
  
  int degrees1, degrees2, degrees3;
  readFlexData(&degrees1, &degrees2, &degrees3); 
  
  sprintf(str, "%d\t%d\t%d\t%d\t%d\t%d", ax, ay, az, degrees1, degrees2, degrees3);
  // print out the result
  Serial.println(str);
  Serial.flush();

  // blink LED to indicate activity
  blinkState = !blinkState;
  digitalWrite(LED_PIN, blinkState);
  
   // pause before taking the next reading
  delay(1000); 
}

