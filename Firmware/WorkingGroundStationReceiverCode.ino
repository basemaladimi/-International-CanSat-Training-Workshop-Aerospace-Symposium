#include <esp_now.h>
#include <WiFi.h>

// ====== Define same struct as sender ======
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

struct_message incomingData;

// ====== ESP-NOW receive callback ======
void OnDataRecv(const esp_now_recv_info_t *recv_info, const uint8_t *data, int dataLen) {
  memcpy(&incomingData, data, sizeof(incomingData));
  Serial.println("=== RECEIVED SENSOR DATA ===");
  Serial.printf("Accel (m/s²): %.2f, %.2f, %.2f\n", incomingData.ax_g, incomingData.ay_g, incomingData.az_g);
  Serial.printf("Gyro (°/s): %.2f, %.2f, %.2f\n", incomingData.gx_dps, incomingData.gy_dps, incomingData.gz_dps);
  Serial.printf("Temp: %.2f °C\n", incomingData.temperatureC);
  Serial.printf("Press: %.2f hPa\n", incomingData.pressureHpa);
  Serial.printf("Alt: %.2f m\n", incomingData.altitudeM);
  Serial.printf("Mag: %.2f, %.2f, %.2f\n", incomingData.mx, incomingData.my, incomingData.mz);
  Serial.printf("Heading: %.2f °\n", incomingData.headingDeg);
  Serial.printf("GPS -> Lat: %.6f, Lon: %.6f, Sats: %d, HDOP: %.1f, Alt: %.2f m, Spd: %.2f km/h, Time: %s\n",
                incomingData.gpsLat, incomingData.gpsLon,
                incomingData.gpsSats, incomingData.gpsHdop,
                incomingData.gpsAlt, incomingData.gpsSpd,
                incomingData.gpsTime);
  Serial.print("Bytes received: "); Serial.println(dataLen);

  // Optional: print sender MAC address
  Serial.print("From: ");
  for (int i = 0; i < 6; ++i) {
    Serial.printf("%02X", recv_info->src_addr[i]);
    if (i < 5) Serial.print(":");
  }
  Serial.println();
  Serial.println("-----------------------");
}

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  if (esp_now_init() != ESP_OK) {
    Serial.println("ESP-NOW init failed");
    return;
  }
  esp_now_register_recv_cb(OnDataRecv);
}

void loop() {
  // Nothing here; everything is in the callback
}