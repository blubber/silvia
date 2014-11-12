
#ifndef __Adafruit_MAX31855
#define __Adafruit_MAX31855 1


class Adafruit_MAX31855 {
  public:
    Adafruit_MAX31855(int8_t SCLK, int8_t CS, int8_t MISO);

    double readInternal(void);
    double readCelsius(void);
    double readFarenheit(void);
    uint8_t readError();

  private:
    int8_t sclk, miso, cs;
    uint32_t spiread32(void);
};

#endif
