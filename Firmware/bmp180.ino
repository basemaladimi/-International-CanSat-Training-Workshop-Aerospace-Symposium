#include <Wire.h>
#include <Adafruit_BMP085.h> // BMP180 library

Adafruit_BMP085 bmp;

// You can set your local sea level pressure here for best accuracy
#define SEA_LEVEL_PRESSURE 101325 // Pa (standard); update with your local value if possible

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22); // ESP32 I2C pins
  if (!bmp.begin()) {
    Serial.println("BMP180 sensor not found!");
    while (1);
  }
  Serial.println("BMP180 initialized. Reading data...");
}

void loop() {
  float temperature = bmp.readTemperature(); // in Celsius
  int32_t pressure = bmp.readPressure();     // in Pa
  float altitude = bmp.readAltitude(SEA_LEVEL_PRESSURE); // in meters

  Serial.print("Temperature (C): ");
  Serial.print(temperature, 2);

  Serial.print("\tPressure (hPa): ");
  Serial.print(pressure / 100.0, 2);

  Serial.print("\tAltitude (m): ");
  Serial.println(altitude, 2);

  delay(1000);
}