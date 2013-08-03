#include "JhaneDataStructure.h"

void initSensorsData(SensorsData* sd){
  (*sd).ax_min= (*sd).ay_min= (*sd).az_min= (*sd).ax_max= (*sd).ay_max= (*sd).az_max= 0;
    for(int i=0; i< FLEX_COUNT; i++){
      (*sd).flexDataMin[i] = (*sd).flexDataMax[i] =0;
    }
}


void initSystemState(SystemState* ss){
  (*ss).isCalibration = false;
}
