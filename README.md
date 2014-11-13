Silvia
======

A do-it-yourself PID controller for the Rancilio Silvia v3 espresso machine.

Goal
----
The original temperature controller in the Silvia uses a bimetallic thermostat to regulate the boiler temperature. The performance of the thermostat can be improved by replacing the bimetallic thermostat with a better thermostat There are various websites describing the process of installing a PID controller in Silvia, some even selling conversion kits. These conversion kits are quite expensive and do not allow the logging of the temperature, which would provide insight in the water temperature. This repository contains code and documentation of our attempt to add a relatively cheap do-it-yourself PID thermostat to Silvia.

Approach
--------
Most kits use an off-the-shelf PID controller unit. We opted to use a microcontroller instead and implement the PID controller in software. This approach is flexible and also allows easy logging of the measurements and controller performance.

Connection & Placement
----------------------
The bimetallic thermostat on the boiler responsive for regulating the water temperature is removed and its function is taken over the by the solid state relay, the wires previously connected to the bimetallic thermostat are now connected to the solid state relay. The removal of this thermostat also allows the use of its screw to hold down the thermocouple at the top of the boiler. Ample space for mounting the solid state relay and controller is found under the water reservoir, next to the water pump.

Used Hardware
-------------
 - Teensy 3.x http://www.pjrc.com/teensy/index.html
 - Thermocouple Amplifier MAX31855 http://www.adafruit.com/products/269
 - Thermocouple Type-K http://www.adafruit.com/products/270
 - Opto 22 240V 25A Solid State Relay http://nl.farnell.com/opto-22/240d25/relay-solid-state-dc-25a-280vac/dp/1839015