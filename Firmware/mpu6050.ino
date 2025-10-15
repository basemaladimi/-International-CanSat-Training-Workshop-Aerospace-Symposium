#include <Wire.h>
#include <MPU6050.h>

MPU6050 accelgyro;

int16_t ax, ay, az;
int16_t gx, gy, gz;

// Earth gravity in m/s²
const float g = 9.80665;

void setup() {
    Wire.begin(21, 22);
    Serial.begin(38400);

    Serial.println("Initializing I2C devices...");
    accelgyro.initialize();

    Serial.println("Testing device connections...");
    Serial.println(accelgyro.testConnection() ? "MPU6050 connection successful" : "MPU6050 connection failed");

    //accelgyro.initialize(MPU6050_ACCEL_FS_4, MPU6050_GYRO_FS_2000);

  //  accelgyro.initialize();
    // Print table header
    Serial.println("Accel (m/s²)\t\tGyro (°/s)");
    Serial.println("X\t\tY\t\tZ\t\tX\t\tY\t\tZ");
}

void loop() {
    accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

    // Convert raw values to g and deg/s
    float ax_g = (ax /1);
    float ay_g = (ay / 1);
    float az_g = (az / 1);

    float gx_dps = gx / 131;
    float gy_dps = gy / 131;
    float gz_dps = gz / 131;



    // Print with fixed width for alignment
    Serial.print(String(ax_g, 2)); Serial.print("\t");
    Serial.print(String(ay_g, 2)); Serial.print("\t");
    Serial.print(String(az_g, 2)); Serial.print("\t");
    Serial.print(String(gx_dps, 2)); Serial.print("\t");
    Serial.print(String(gy_dps, 2)); Serial.print("\t");
    Serial.println(String(gz_dps, 2));

    delay(100);
}