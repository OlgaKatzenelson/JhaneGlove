#include "JhaneDataStructure.h"

void initSensorsData(SensorsData* sd){
  (*sd).ax_min= -17000;
  (*sd).ay_min= -8500;
  (*sd).az_min= -20000;
  (*sd).ax_max= 17000;
  (*sd).ay_max= 9000;
  (*sd).az_max= 15000;
  
   (*sd).flexDataMin[0] = 517;
   (*sd).flexDataMax[0] = 646;
   (*sd).flexDataMin[1] = 530;
   (*sd).flexDataMax[1] = 615;
   (*sd).flexDataMin[2] = 500;
   (*sd).flexDataMax[2] = 620;
      
//    for(int i=0; i< FLEX_COUNT; i++){
//      (*sd).flexDataMin[i] = 510;
//      (*sd).flexDataMax[i] = 610;
//    }
}


void initSystemState(SystemState* ss){
  (*ss).isCalibration = false;
}

int16_t calMap(int16_t val, int16_t minVal, int16_t maxVal, int16_t absMin, int16_t absMax){
  int16_t newVal = map(val, minVal, maxVal, absMin, absMax);
  if(newVal < absMin){
      newVal = absMin;
  }
  
  if(newVal > absMax){
      newVal = absMax;
  }
  return newVal;
}

