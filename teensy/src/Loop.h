#ifndef __LOOP_H_
#define __LOOP_H_ 1

#include <stdint.h>

#include "Stream.h"
#include "Controller.h"


typedef enum {
    COMMAND_STATUS1        = 1,
    COMMAND_STATUS2        = 2,
    COMMAND_STATUS3        = 3,
    COMMAND_SETPOINT       = 10,
    COMMAND_START_PUMP     = 20,
    COMMAND_STOP_PUMP      = 21,
} CommandType;


class ITemperatureSensor {
  public:
    virtual double readTemperature () = 0;
};


class Loop {

  public:
    Loop (Stream &stream, AbstractController &controller, ITemperatureSensor &sensor):
        stream(stream), controller(controller), sensor(sensor) {};
    Loop (Stream &stream, AbstractController &controller, ITemperatureSensor &sensor, uint16_t full_cycle):
        stream(stream), controller(controller), sensor(sensor), full_cycle(full_cycle) {};

    void          once              (uint32_t);
    void          setFullCycle      (uint16_t cycle) { full_cycle = cycle; };
    int           getHeaterOn       ()  { return heater_on; };
    int           getPumpOn         ()  { return pump_on; };

  private:
    Stream              &stream;
    AbstractController  &controller;
    ITemperatureSensor  &sensor;

    uint16_t             full_cycle        = 0,
                         heater_on_cycle   = 0,
                         heater_off_cycle  = 0,
                         dt                = 0;

    uint32_t             first_call        = 0,
                         last_call         = 0,
                         pump_on_cycle     = 0;

    double               temperature       = 0.0,
                         heater_power      = 0.0;

    int                  heater_on         = 0,
                         pump_on           = 0;

    void                 setHeaterPower (uint32_t);
    void                 setPumpCycle   ();
    void                 pollComms      ();
};


#endif
