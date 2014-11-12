
# The name of your project (used to name the compiled .hex file)
TARGET = main

# Path to your arduino installation
ARDUINOPATH ?= /Applications/Arduino.app/Contents/Resources/Java/

# configurable options
OPTIONS = -DF_CPU=48000000 -DUSB_SERIAL -DLAYOUT_US_ENGLISH

# options needed by many Arduino libraries to configure for Teensy 3.0
OPTIONS += -D__MK20DX128__ -DARDUIO=105 -DTEENSYDUINO=118


# Other Makefiles and project templates for Teensy 3.x:
#
# https://github.com/apmorton/teensy-template
# https://github.com/xxxajk/Arduino_Makefile_master
# https://github.com/JonHylands/uCee


#************************************************************************
# Location of Teensyduino utilities, Toolchain, and Arduino Libraries.
# To use this makefile without Arduino, copy the resources from these
# locations and edit the pathnames.  The rest of Arduino is not needed.
#************************************************************************

# path location for Teensy Loader, teensy_post_compile and teensy_reboot
TOOLSPATH = $(ARDUINOPATH)/hardware/tools   # on Linux
#TOOLSPATH = $(ARDUINOPATH)/hardware/tools/tools/avr/bin   # on Mac or Windows

# path location for Arduino libraries (currently not used)
LIBRARYPATH = $(ARDUINOPATH)/libraries

# path location for the arm-none-eabi compiler
COMPILERPATH = $(ARDUINOPATH)/hardware/tools/arm-none-eabi/bin

#************************************************************************
# Settings below this point usually do not need to be edited
#************************************************************************

# CPPFLAGS = compiler options for C and C++
CPPFLAGS = -Wall -g -Os -mcpu=cortex-m4 -mthumb -nostdlib -MMD $(OPTIONS) -I. -Iteensy3/

# compiler options for C++ only
CXXFLAGS = -std=gnu++0x -felide-constructors -fno-exceptions -fno-rtti

# compiler options for C only
CFLAGS =

# linker options
LDFLAGS = -Os -Wl,--gc-sections -mcpu=cortex-m4 -mthumb -Tteensy3/mk20dx128.ld

# additional libraries to link
LIBS = -lm

CORE_C_SRCS     = $(wildcard teensy3/*.c)
CORE_CPP_SRCS   = $(wildcard teensy3/*.cpp)
CORE_OBJ_FILES  = $(CORE_C_SRCS:.c=.o) $(CORE_CPP_SRCS:.cpp=.o)

# names for the compiler programs
CC = $(abspath $(COMPILERPATH))/arm-none-eabi-gcc
CXX = $(abspath $(COMPILERPATH))/arm-none-eabi-g++
OBJCOPY = $(abspath $(COMPILERPATH))/arm-none-eabi-objcopy
SIZE = $(abspath $(COMPILERPATH))/arm-none-eabi-size

# automatically create lists of the sources and objects
# TODO: this does not handle Arduino libraries yet...
C_FILES := $(wildcard *.c)
CPP_FILES := $(wildcard *.cpp)
#OBJS := $(C_FILES:.c=.o) $(CPP_FILES:.cpp=.o)

OBJS := $(C_FILES:.c=.o) $(CPP_FILES:.cpp=.o) $(CORE_OBJ_FILES:.c=.o) Adafruit-MAX31855-library/Adafruit_MAX31855.o


# the actual makefile rules (all .o files built by GNU make's default implicit rules)

all: upload

$(TARGET).elf: $(OBJS) teensy3/mk20dx128.ld
	$(CC) $(LDFLAGS) -o $@ $(OBJS) $(LIBS)
	let NEW_VERSION=`awk  '/ VERSION / { print $$3; }' version.h`+1 && sed -i.bak -e "s/define VERSION [0-9][0-9]*/define VERSION $$NEW_VERSION/" version.h

%.hex: %.elf
	$(SIZE) $<
	$(OBJCOPY) -O ihex -R .eeprom $< $@

upload: $(TARGET).hex
	$(abspath $(TOOLSPATH))/teensy_post_compile -file=$(basename $<) -path=$(shell pwd) -tools=$(abspath $(TOOLSPATH))
	-$(abspath $(TOOLSPATH))/teensy_reboot


# compiler generated dependency info
-include $(OBJS:.o=.d)

clean:
	rm -f *.o *.d $(TARGET).elf $(TARGET).hex

dist-clean: clean
	rm -rf teensy3/

teensy3:
	mkdir teensy3
	cp -rf $(ARDUINOPATH)hardware/teensy/cores/teensy3/* \
		teensy3/
	cp -rf $(ARDUINOPATH)libraries/SPI/* teensy3/
	rm -rf teensy3/Makefile teensy3/main*

teensy-core/%.o: %.c
	$(CC) -c $(CPPFLAGS) $(CFLAGS) $< -o $@

teensy-core/%.o: %.cpp
	$(CXX) -c $(CPPFLAGS) $(CXXFLAGS) $< -o $@

Adafruit-MAX31855-library/%.o: %.cpp
	$(CXX) -c $(CPPFLAGS) $(CXXFLAGS) $< -o $@
