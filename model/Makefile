
all: libcontroller.so

libcontroller.so: controller.o
	gcc -I../teensy -shared controller.o -o libcontroller.so


controller.o: ../teensy/controller.c
	gcc -I../teensy -c ../teensy/controller.c -o controller.o -fPIC

clean:
	rm -f libcontroller.so controller.o
