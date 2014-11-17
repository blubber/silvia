
#include "WProgram.h"
#include "Adafruit-MAX31855-library/Adafruit_MAX31855.h"

extern "C" {
    #include "controller.h"
}
#include "version.h"


// --------------------------------------------------------------------------
// The setpoint in degrees Celsius
#define SETPOINT         100


#define CYCLE            500



// --------------------------------------------------------------------------
// PID controller parameters.
#define KP               0.065
#define KI               0
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
    uint32_t last_millis = 0, now, cycle, sleep;
    float    output, T, dt;
    int      heating = 1, i = 0;

    Adafruit_MAX31855 thermocouple(THERMO_CLK, THERMO_CS, THERMO_DO);
    ControllerContext ctx = controller_new(SETPOINT, KP, KI, KP);

    Serial.begin(9600);
    pinMode(HEATER_PIN, OUTPUT);
    pinMode(13, OUTPUT);

    digitalWrite(HEATER_PIN, LOW);
    digitalWrite(13, LOW);
    
    for (;;) {
        now = millis();

        if (now >= (3600 * 1000)) {
            heating = 0;
        }

        dt = (float)now - (float)last_millis;
        last_millis = now;
        T = read_sensor(thermocouple);
        output = controller_power(&ctx, dt, T);
        cycle = (uint32_t)(CYCLE * (output > 1 ? 1 : (output < 0 ? 0 : output)));

        if (++i == 10) {
            i = 0;
            Serial.print(":Kp=");        Serial.print(KP);
            Serial.print("Ki=");        Serial.print(KI);
            Serial.print(" Kd=");       Serial.print(KD);
            Serial.print(" setpoint="); Serial.print(SETPOINT);
            Serial.print(" cycle=");    Serial.println(CYCLE);

            Serial.println(":On\tT\tOut\tdt\tCyc\tms");
        }

        Serial.print(heating); Serial.print("\t");
        Serial.print(T);       Serial.print("\t");
        Serial.print(output);  Serial.print("\t");
        Serial.print(dt);      Serial.print("\t");
        Serial.print(cycle);   Serial.print("\t");
        Serial.println(now);        

        if (heating == 1) {
            digitalWrite(HEATER_PIN, HIGH);
            digitalWrite(13, HIGH);
        }
        delay(cycle);

        digitalWrite(HEATER_PIN, LOW);
        digitalWrite(13, LOW);
        delay(CYCLE - cycle);
    }
}
