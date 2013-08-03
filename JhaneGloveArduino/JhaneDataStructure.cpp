#include "JhaneDataStructure.h"

void initSensorsData(SensorsData* sd){
  (*sd).ax_min= (*sd).ay_min= (*sd).az_min= -15000;
  (*sd).ax_max= (*sd).ay_max= (*sd).az_max= 15000;
    for(int i=0; i< FLEX_COUNT; i++){
      (*sd).flexDataMin[i] = 510;
      (*sd).flexDataMax[i] = 610;
    }
}


void initSystemState(SystemState* ss){
  (*ss).isCalibration = false;
}
