#ifndef JHANE_DATA_STRUCTURE
#define JHANE_DATA_STRUCTURE

#include "MPU6050.h"
#define FLEX_COUNT 3
#define FLEX_MAX_RANGE 90
#define ACC_MAX_RANGE 255

struct sensorsData 
  {
      int16_t ax, ay, az;
      int16_t gx, gy, gz;
      int16_t ax_min, ay_min, az_min, ax_max, ay_max, az_max;
      int16_t flexData[FLEX_COUNT];
      int16_t flexDataMin[FLEX_COUNT];
      int16_t flexDataMax[FLEX_COUNT];
  };
  
  struct systemState 
  {
      bool isCalibration;
  };
  
  enum StateType               // Declare enum type StateType
  {
     calibrationStarted,            
     calibratedMinValues,          
     calibratedMaxValues
  };
  

  const String StateStrings[] =   
  {
    "calStart",            
     "min:",          
     "max:"
  };
  
 typedef struct sensorsData SensorsData; 
 typedef struct systemState SystemState; 
 
 void initSensorsData(SensorsData* sd);
 void initSystemState(SystemState* ss);

#endif
