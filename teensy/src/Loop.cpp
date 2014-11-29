
#include "Loop.h"

#define PACK16(a, n, o) a[0+o] = n >> 8; a[1+o] = n & 0xff
#define PACK32(a, n, o) a[0+o] = n >> 24; a[1+o] = n >> 16; a[2+o] = n >> 8; a[3+o] = n & 0xff
#define PACKF(a, f, o) a[0+o] = (uint8_t)f; a[1+o] = (uint8_t)(255 * (f - (uint8_t)f));

void Loop::once (uint32_t now) {
    if (full_cycle == 0) {
        return;
    }

    if (first_call == 0) {
        first_call = now;
        return;
    }

    setHeaterPower(now);
    setPumpCycle();
    pollComms();
}


void Loop::setHeaterPower (uint32_t now) {
    if (heater_on_cycle > 0) {
        heater_on = 1;
        heater_on_cycle--;
    } else if (heater_off_cycle > 9) {
        heater_on = 0;
        heater_off_cycle--;
    } else {
        temperature = sensor.readTemperature();
        dt = now - last_call;
        last_call = now;
        heater_power = controller.heaterPower((double)(dt / 1000.0),
                                              temperature);

        if (heater_power >= 1) {
            heater_on = 1;
            heater_on_cycle = full_cycle;
            heater_off_cycle = 0;
        } else if (heater_power == 0) {
            heater_on = 0;
            heater_on_cycle = 0;
            heater_off_cycle = full_cycle;
        } else {
            heater_on_cycle = (uint16_t)(heater_power * full_cycle);
            heater_off_cycle = full_cycle - heater_on_cycle;
            heater_on = 1;
        }
    }
}


void Loop::setPumpCycle () {
    if (pump_on_cycle > 0) {
        pump_on = 1;
        pump_on_cycle--;
    } else {
        pump_on = 0;
    }
}


void Loop::pollComms () {
    uint8_t buf[8];
    uint8_t output[8] = { 0 };
    double current_setpoint;

    if (stream.available() >= 8) {
        stream.readBytes(buf, 8);
        output[0] = buf[0];

        switch (buf[0]) {
            case COMMAND_STATUS1:
                PACK16(output, heater_on_cycle, 1);
                PACK16(output, heater_off_cycle, 3);
                PACK16(output, dt, 5);
                output[7] = heater_on & 0xff;
                break;

            case COMMAND_STATUS2:
                PACK32(output, pump_on_cycle, 1);
                PACKF(output, temperature, 5);
                output[7] = pump_on & 0xff;
                break;

            case COMMAND_STATUS3:
                PACKF(output, heater_power, 1);
                break;

            case COMMAND_SETPOINT:
                current_setpoint = controller.getSetpoint();
                controller.setSetpoint(buf[1] + buf[2] / 255.0);
                PACKF(output, controller.getSetpoint(), 1);
                PACKF(output, current_setpoint, 3);
                break;

            case COMMAND_START_PUMP:
                pump_on_cycle = (buf[1] << 8) + buf[2];
                break;

            case COMMAND_STOP_PUMP:
                pump_on_cycle = 0;
                break;

        }

        stream.write(output, 8);
    }
}
