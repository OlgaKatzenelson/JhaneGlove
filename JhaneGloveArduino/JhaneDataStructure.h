#ifndef JHANE_DATA_STRUCTURE
#define JHANE_DATA_STRUCTURE

#include "MPU6050.h"
#define FLEX_COUNT 5
#define FINGERS_COUNT 4
#define FLEX_MAX_RANGE 90
#define COM_MAX_RANGE 90
#define ACC_MAX_RANGE 90 //255

struct sensorsData 
  {
      int16_t ax, ay, az;
      int16_t gx, gy, gz;
      int16_t ax_min, ay_min, az_min, ax_max, ay_max, az_max;
      int16_t flexData[FLEX_COUNT];
      int16_t flexDataMin[FLEX_COUNT];
      int16_t flexDataMax[FLEX_COUNT];
      int firstPhalange[FINGERS_COUNT];
      int secondPhalange[FINGERS_COUNT];
      int palm[FINGERS_COUNT];
  };
  
  struct systemState 
  {
      bool isCalibration;
      bool fullData;
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
 int16_t calMap(int16_t val, int16_t minVal, int16_t maxVal, int16_t absMin, int16_t absMax);

#endif
