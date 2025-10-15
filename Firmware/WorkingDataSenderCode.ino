#include <Wire.h>
#include <MPU6050.h>
#include <Adafruit_BMP085.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_HMC5883_U.h>
#include <SPI.h>
#include <SD.h>
#include <TinyGPSPlus.h>
#include <esp_now.h>
#include <WiFi.h>

// ====== ESP-NOW Receiver MAC ======
uint8_t broadcastAddress[] = {0x00, 0x4b, 0x12, 0x3a, 0x4c, 0x84}; // <-- EDIT THIS for your receiver

// ====== Define payload struct ======
typedef struct struct_message {
  float ax_g, ay_g, az_g;
  float gx_dps, gy_dps, gz_dps;
  float temperatureC, pressureHpa, altitudeM;
  float mx, my, mz, headingDeg;
  double gpsLat, gpsLon;
  int gpsSats;
  double gpsHdop, gpsAlt, gpsSpd;
  char gpsTime[16];
} struct_message;

struct_message outgoingData;

// ====== Sensor definitions ======
MPU6050 accelgyro;
Adafruit_BMP085 bmp;
Adafruit_HMC5883_Unified mag = Adafruit_HMC5883_Unified(12345);

#define SD_CS   5
#define BUZZER  25
File dataFile;
bool sd_ok = false;

#define SEA_LEVEL_PRESSURE_HPA 1013.25
const float g = 9.80665;

// ====== GPS config ======
static const int RXD2 = 16;
static const int TXD2 = 17;
static const uint32_t GPS_BAUD = 9600;
TinyGPSPlus gps;
double gpsLat = 0.0, gpsLon = 0.0;
int gpsSats = 0;
double gpsHdop = 0.0;
double gpsAlt = 0.0;
double gpsSpd = 0.0;
char gpsTime[16] = "--:--:--";

// ====== Sensor/GPS init and read functions ======
void initMPU() {
  Serial.println("MPU6050 init...");
  accelgyro.initialize();
  if (accelgyro.testConnection()) Serial.println("MPU6050 ready!");
  else Serial.println("⚠️ MPU6050 not found!");
}
void initBMP() {
  Serial.println("BMP180 init...");
  if (!bmp.begin()) Serial.println("⚠️ Could not find BMP180 sensor!");
  else Serial.println("BMP180 ready!");
}
void initHMC() {
  Serial.println("HMC5883L init...");
  if (!mag.begin()) Serial.println("⚠️ Could not find HMC5883L sensor!");
  else Serial.println("HMC5883L ready!");
}
void initSD() {
  Serial.println("SD card init...");
  if (!SD.begin(SD_CS)) {
    Serial.println("⚠️ SD init failed! Data will NOT be saved.");
    tone(BUZZER, 400, 1000);
    sd_ok = false;
    return;
  }
  Serial.println("SD card ready.");
  sd_ok = true;
  dataFile = SD.open("/data.csv", FILE_WRITE);
  if (dataFile) {
    dataFile.println("ax(ms2),ay(ms2),az(ms2),gx(dps),gy(dps),gz(dps),temperatureC,pressure_hPa,altitude_m,magX,magY,magZ,heading_deg,lat,lon,sats,hdop,alt_gps,spd,time");
    dataFile.close();
  } else {
    Serial.println("⚠️ Failed to open data.csv");
    sd_ok = false;
  }
}
void initGPS() {
  Serial.println("GPS init...");
  Serial2.begin(GPS_BAUD, SERIAL_8N1, RXD2, TXD2);
  Serial.println("Waiting for GPS data...");
}
void readGPS() {
  while (Serial2.available()) gps.encode(Serial2.read());
  if (gps.location.isValid()) {
    gpsLat = gps.location.lat();
    gpsLon = gps.location.lng();
  }
  gpsSats = gps.satellites.isValid() ? gps.satellites.value() : 0;
  gpsHdop = gps.hdop.isValid() ? gps.hdop.hdop() : 0.0;
  gpsAlt = gps.altitude.isValid() ? gps.altitude.meters() : 0.0;
  gpsSpd = gps.speed.isValid() ? gps.speed.kmph() : 0.0;
  if (gps.time.isValid()) {
    snprintf(gpsTime, sizeof(gpsTime), "%02d:%02d:%02d", gps.time.hour(), gps.time.minute(), gps.time.second());
  } else {
    strcpy(gpsTime, "--:--:--");
  }
}
void readSensors(float &ax_g, float &ay_g, float &az_g,
                 float &gx_dps, float &gy_dps, float &gz_dps,
                 float &temperatureC, float &pressureHpa, float &altitudeM,
                 float &mx, float &my, float &mz, float &headingDeg) {
  int16_t ax, ay, az, gx, gy, gz;
  accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
  ax_g = ((float)ax / 16384.0) * g;
  ay_g = ((float)ay / 16384.0) * g;
  az_g = ((float)az / 16384.0) * g;
  gx_dps = gx / 131.0;
  gy_dps = gy / 131.0;
  gz_dps = gz / 131.0;
  float pressurePa = bmp.readPressure();
  temperatureC = bmp.readTemperature();
  pressureHpa = pressurePa / 100.0f;
  altitudeM = bmp.readAltitude(SEA_LEVEL_PRESSURE_HPA * 100.0f);
  sensors_event_t event;
  mag.getEvent(&event);
  mx = event.magnetic.x;
  my = event.magnetic.y;
  mz = event.magnetic.z;
  float heading = atan2(my, mx);
  if (heading < 0) heading += 2 * PI;
  headingDeg = heading * 180 / M_PI;
}
void printData(float ax_g, float ay_g, float az_g,
               float gx_dps, float gy_dps, float gz_dps,
               float temperatureC, float pressureHpa, float altitudeM,
               float mx, float my, float mz, float headingDeg) {
  Serial.println("=== SENSOR DATA ===");
  Serial.printf("Accel (m/s²): %.2f, %.2f, %.2f\n", ax_g, ay_g, az_g);
  Serial.printf("Gyro (°/s): %.2f, %.2f, %.2f\n", gx_dps, gy_dps, gz_dps);
  Serial.printf("Temp: %.2f °C\n", temperatureC);
  Serial.printf("Press: %.2f hPa\n", pressureHpa);
  Serial.printf("Alt: %.2f m\n", altitudeM);
  Serial.printf("Mag: %.2f, %.2f, %.2f\n", mx, my, mz);
  Serial.printf("Heading: %.2f °\n", headingDeg);
  Serial.printf("GPS -> Lat: %.6f, Lon: %.6f, Sats: %d, HDOP: %.1f, Alt: %.2f m, Spd: %.2f km/h, Time: %s\n",
                gpsLat, gpsLon, gpsSats, gpsHdop, gpsAlt, gpsSpd, gpsTime);
  Serial.println("-----------------------");
}
void logToSD(float ax_g, float ay_g, float az_g,
             float gx_dps, float gy_dps, float gz_dps,
             float temperatureC, float pressureHpa, float altitudeM,
             float mx, float my, float mz, float headingDeg) {
  if (!sd_ok) return;
  dataFile = SD.open("/data.csv", FILE_APPEND);
  if (dataFile) {
    dataFile.printf("%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.6f,%.6f,%d,%.1f,%.2f,%.2f,%s\n",
                    ax_g, ay_g, az_g, gx_dps, gy_dps, gz_dps,
                    temperatureC, pressureHpa, altitudeM,
                    mx, my, mz, headingDeg,
                    gpsLat, gpsLon, gpsSats, gpsHdop, gpsAlt, gpsSpd, gpsTime);
    dataFile.close();
  } else {
    Serial.println("⚠️ Error writing to data.csv");
    tone(BUZZER, 500, 2000);
  }
}

// ====== ESP-NOW callbacks ======
void OnDataSent(const wifi_tx_info_t *info, esp_now_send_status_t status) {
  Serial.print("Send Status: ");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Success" : "Fail");
}

// ====== Setup ======
void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);
  initMPU();
  initBMP();
  initHMC();
  initSD();
  initGPS();

  WiFi.mode(WIFI_STA);
  if (esp_now_init() != ESP_OK) {
    Serial.println("ESP-NOW init failed");
    return;
  }
  esp_now_register_send_cb(OnDataSent);
  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;
  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("Peer add failed");
    return;
  }
}

// ====== Loop ======
void loop() {
  float ax_g, ay_g, az_g, gx_dps, gy_dps, gz_dps;
  float temperatureC, pressureHpa, altitudeM;
  float mx, my, mz, headingDeg;
  readGPS();
  readSensors(ax_g, ay_g, az_g, gx_dps, gy_dps, gz_dps,
              temperatureC, pressureHpa, altitudeM,
              mx, my, mz, headingDeg);
  printData(ax_g, ay_g, az_g, gx_dps, gy_dps, gz_dps,
            temperatureC, pressureHpa, altitudeM,
            mx, my, mz, headingDeg);
  logToSD(ax_g, ay_g, az_g, gx_dps, gy_dps, gz_dps,
          temperatureC, pressureHpa, altitudeM,
          mx, my, mz, headingDeg);

  // Prepare struct and send via ESP-NOW
  outgoingData.ax_g = ax_g; outgoingData.ay_g = ay_g; outgoingData.az_g = az_g;
  outgoingData.gx_dps = gx_dps; outgoingData.gy_dps = gy_dps; outgoingData.gz_dps = gz_dps;
  outgoingData.temperatureC = temperatureC; outgoingData.pressureHpa = pressureHpa; outgoingData.altitudeM = altitudeM;
  outgoingData.mx = mx; outgoingData.my = my; outgoingData.mz = mz; outgoingData.headingDeg = headingDeg;
  outgoingData.gpsLat = gpsLat; outgoingData.gpsLon = gpsLon; outgoingData.gpsSats = gpsSats;
  outgoingData.gpsHdop = gpsHdop; outgoingData.gpsAlt = gpsAlt; outgoingData.gpsSpd = gpsSpd;
  strncpy(outgoingData.gpsTime, gpsTime, sizeof(outgoingData.gpsTime));

  esp_err_t result = esp_now_send(broadcastAddress, (uint8_t *)&outgoingData, sizeof(outgoingData));
  if (result == ESP_OK) Serial.println("ESP-NOW: Data sent!");
  else Serial.println("ESP-NOW: Send error");

  delay(10);
}