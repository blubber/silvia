
#include "WProgram.h"
#include "Adafruit-MAX31855-library/Adafruit_MAX31855.h"

#include "version.h"


// --------------------------------------------------------------------------
// The setpoint in degrees Celsius
#define SETPOINT         100



// --------------------------------------------------------------------------
// PID controller parameters.
#define KP               0.025
#define KI               0.0001
#define KD               0


// --------------------------------------------------------------------------
// Pins used by the thermocouple
#define THERMO_DO        21
#define THERMO_CS        20
#define THERMO_CLK       19


// --------------------------------------------------------------------------
// Pin used to control the heating element
#define HEATER_PIN       0


  
double read_sensor (Adafruit_MAX31855 thermocouple) {
    return thermocouple.readCelsius();
}

extern "C" int main(void) {
    int      cycle;
    uint32_t last_millis, now;
    double   dt             = 0;
    double   previous_error = 0;
    double   error          = 0;
    double   output         = 0;
    double   derivative     = 0;
    double   integral       = 0;
    double   measured_value;

    Adafruit_MAX31855 thermocouple(THERMO_CLK, THERMO_CS, THERMO_DO);


    Serial.begin(9600);
    pinMode(HEATER_PIN, OUTPUT);
    pinMode(13, OUTPUT);

    digitalWrite(HEATER_PIN, LOW);
    digitalWrite(13, LOW);
    
	while (1) {
        now = millis();
        dt = (now - last_millis) / (double)1000;
        last_millis = now;

        measured_value = read_sensor(thermocouple);

        if (isnan(measured_value)) {
            measured_value = 250;
        }

        error = SETPOINT - measured_value;
        integral = integral + error * dt;

        if (dt == 0) {
            derivative = 0;
        } else {
            derivative = (error - previous_error) / dt;
        }

        output = KP * error + KI * integral + KD * derivative;
        previous_error = error;

        cycle = (int)(500 * constrain(output, 0, 1));
        
        Serial.print(VERSION); Serial.print(" ");
        Serial.print(measured_value); Serial.print(" ");
        Serial.print(output); Serial.print(" ");
        Serial.print(integral); Serial.print(" ");
        Serial.print(error); Serial.print(" ");
        Serial.print(dt); Serial.print(" ");
        Serial.println(cycle);
        
        digitalWrite(HEATER_PIN, HIGH);
        digitalWrite(13, HIGH);
        delay(cycle);

        digitalWrite(HEATER_PIN, LOW);
        digitalWrite(13, LOW);
        delay(500 - cycle);
    }
}
