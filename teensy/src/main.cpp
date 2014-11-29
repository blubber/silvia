
#include "WProgram.h"
#include "Adafruit-MAX31855-library/Adafruit_MAX31855.h"

#include "Loop.h"
#include "Controller.h"
#include "version.h"
#include "config.h"


IntervalTimer timer;
volatile int tick = 0;


void set_tick () {
    __disable_irq();
    tick = 1;
    __enable_irq();
}


class AdaFruitSensor: public ITemperatureSensor {
  public:
    AdaFruitSensor(Adafruit_MAX31855 _sensor): sensor(_sensor) {};
    double readTemperature () { return sensor.readCelsius(); };

  private:
    Adafruit_MAX31855 &sensor;
};


extern "C" int main(void) {
    PidController     controller(SETPOINT, KP, KI, KD);
    AdaFruitSensor    sensor(Adafruit_MAX31855(THERMO_CLK, THERMO_CS, THERMO_DO));
    Loop              loop(Serial, controller, sensor, CYCLE);
    int               tick_ = 0;

    // Configure heater, pump and led pin
    pinMode(HEATER_PIN, OUTPUT);
    pinMode(PUMP_PIN, OUTPUT);
    pinMode(13, OUTPUT);

    digitalWrite(HEATER_PIN, LOW);
    digitalWrite(PUMP_PIN, LOW);
    digitalWrite(13, HIGH);

    // Init serial and delay to allow programming.
    Serial.begin(9600);
    delay(2500);

    timer.begin(set_tick, 1000);

    for (;;) {
        __disable_irq();
        tick_ = tick;
        tick = 0;
        __enable_irq();

        if (tick_ == 1) {
            loop.once(millis());
            digitalWrite(HEATER_PIN, loop.getHeaterOn());
            digitalWrite(PUMP_PIN, loop.getPumpOn());
        }
    }
}
