// Arduino Wire library is required if I2Cdev I2CDEV_ARDUINO_WIRE implementation
// is used in I2Cdev.h
#include "Wire.h"

#include "I2Cdev.h"
#include "MPU6050.h"

#include "JhaneDataStructure.h"

#define LED_PIN 13
#define FLEX_PIN_1 0
#define FLEX_PIN_2 1
#define FLEX_PIN_3 9
#define FLEX_PIN_4 2
#define FLEX_PIN_5 8

MPU6050 accelgyro;

SensorsData sd;
SystemState state;
char str[512];

bool blinkState = false;

void setup();
void loop();

void readFlexData(int* degrees1, int* degrees2, int* degrees3, int* degrees4, int* degrees5){
  //flex3 and flex5 has special processing
  int flex1, flex2, flex3, flex4, flex5;
  // read the voltage from the voltage divider (sensor plus resistor)
  flex1 = analogRead(FLEX_PIN_1);
  flex2 = analogRead(FLEX_PIN_2);
  flex4 = analogRead(FLEX_PIN_4);
  flex5 = readMux(FLEX_PIN_5);
  
  if(state.isCalibration){
      *degrees1 = flex1;
      *degrees2 = flex2;
      *degrees4 = flex4;
      *degrees5 = flex5;
  }else{
      // convert the voltage reading to inches
      // the first two numbers are the sensor values for straight (510) and bent (610)
      // the second two numbers are the degree readings we'll map that to (0 to 90 degrees)
//      *degrees1 = map(flex1, 510, 610, 0, 90);
      *degrees1 = calMap(flex1, sd.flexDataMin[0], sd.flexDataMax[0], 0, FLEX_MAX_RANGE);
      *degrees2 = calMap(flex2, sd.flexDataMin[1], sd.flexDataMax[1], 0, FLEX_MAX_RANGE);
      *degrees4 = calMap(flex4, sd.flexDataMin[3], sd.flexDataMax[3], 0, FLEX_MAX_RANGE);
     
     if(flex5 > sd.flexDataMax[4]+5 && flex5 < sd.flexDataMax[4]+10){
       *degrees5 = FLEX_MAX_RANGE - 10;
     }else if(flex5 >= sd.flexDataMax[4]+10){
       *degrees5 = FLEX_MAX_RANGE;
     }else{
        *degrees5 = calMap(flex5, sd.flexDataMin[4], sd.flexDataMax[4], 0, FLEX_MAX_RANGE-30);
     }
  }
  
  
  flex3 = readMux(FLEX_PIN_3);
  if(flex3 < 510){
    flex3 = 0;
  }else if(flex3 >=510 && flex3 < 515) {
    flex3 = 30;
  }else if(flex3 >=515 && flex3 < 520) {
    flex3 = 60;
  }else{
    flex3 = 90;
  }
  
  *degrees3 = flex3;
   
   
  
  
  
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
    if(serialDataIn.startsWith(StateStrings[calibratedMinValues]) || serialDataIn.startsWith(StateStrings[calibratedMaxValues])){
        char charBuf[serialDataIn.length()+1];
        serialDataIn.toCharArray(charBuf, serialDataIn.length()+1);
        if(serialDataIn.startsWith(StateStrings[calibratedMinValues])){
           sscanf(charBuf,"min:[%d, %d, %d, %d, %d, %d]\n",&sd.ax_min, &sd.ay_min,&sd.az_min, &sd.flexDataMin[0], &sd.flexDataMin[1], &sd.flexDataMin[2]);
        }else{
           sscanf(charBuf,"max:[%d, %d, %d, %d, %d, %d]\n",&sd.ax_max, &sd.ay_max,&sd.az_max, &sd.flexDataMax[0], &sd.flexDataMax[1], &sd.flexDataMax[2]);
           state.isCalibration = false;
           Serial.println("Ready");
           Serial.flush();
// Serial.print("**************max:");
//          Serial.print(ax_max);
//    Serial.print(flexDataMax[1]);
//    Serial.println(flexDataMax[2]);
//    Serial.flush();
        }
    
    }else if(serialDataIn == StateStrings[calibrationStarted]){
      state.isCalibration = true;
      Serial.println("command:startCalTimestamp");  //after this command arduino strats to send raw data
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
  
  initSensorsData(&sd);
  initSystemState(&state);
  
  comparatorSetup();
}


void loop() {
//  Serial.print("Value at channel ");
//    Serial.print(0);
//    Serial.print("is : ");
//    Serial.println(readMux(0));
//    delay(1000); 
//    Serial.print(1);
//    Serial.print("is : ");
//    Serial.println(readMux(1));

  // read raw accel/gyro measurements from device
  accelgyro.getMotion6(&sd.ax, &sd.ay, &sd.az, &sd.gx, &sd.gy, &sd.gz);
  if(state.isCalibration == false){
    sd.ax = calMap(sd.ax, sd.ax_min, sd.ax_max, 0, ACC_MAX_RANGE);
    sd.ay = calMap(sd.ay, sd.ay_min, sd.ay_max, 0, ACC_MAX_RANGE);
    sd.az = calMap(sd.az, sd.az_min, sd.az_max, 0, ACC_MAX_RANGE);
    
  }
  
  readFlexData(&sd.flexData[0], &sd.flexData[1], &sd.flexData[2], &sd.flexData[3], &sd.flexData[4]); 
 
  
  readMux(sd);
  
  //full version
  sprintf(str, "data:%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d", sd.ax, sd.ay, sd.az,sd.flexData[0], sd.flexData[1], sd.flexData[2],sd.flexData[3], sd.flexData[4], 
        sd.firstPhalange[0], sd.secondPhalange[0], sd.palm[0], sd.firstPhalange[1], sd.secondPhalange[1], sd.palm[1], sd.firstPhalange[2], sd.secondPhalange[2], sd.palm[2], 
        sd.firstPhalange[3], sd.secondPhalange[3], sd.palm[3]);
//        
        
//   sprintf(str, "data:%d\t%d\t%d\t%d\t%d\t%d", sd.flexData[0], sd.flexData[1], sd.flexData[2], sd.firstPhalange[0], sd.secondPhalange[0], sd.palm[0]);

//  sprintf(str, "data:%d\t%d\t%d\t%d\t%d\t%d", sd.ax, sd.ay, sd.az, sd.flexData[0], sd.flexData[1], sd.flexData[2]);
//    sprintf(str, "data:%d\t%d\t%d\t%d\t%d\t%d", sd.ax, sd.ay, sd.az, sd.gx, sd.gy, sd.gz);

  // print out the result
  Serial.println(str);
  Serial.flush();

  // blink LED to indicate activity
  blinkState = !blinkState;
  digitalWrite(LED_PIN, blinkState);
  
   // pause before taking the next reading
  delay(1000); 
}

