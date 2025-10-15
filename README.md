# 🚀 ICESCO International Model Satellite Workshop (CanSat Project) & Aerospace Symposium
This repository serves as my personal documentation of my participation in the ICESCO International Model Satellite Workshop & Aerospace Symposium, where I contributed to building and programming a CanSat (model satellite).
The workshop was organized by ICESCO in Almaty, Kazakhstan, and was supervised by Istanbul Technical University – Space System Design and Testing Laboratory, led by Prof. Alim Rüstem Aslan, Barış Beynek, and Onur Öztekin.

________________________________________________________________________________________________
## Contributors
- **Basem Alademi** [@basemaladimi](https://github.com/basemaladimi)
- **Abalwahab Rais** [@rayis1](https://github.com/rayis1)
________________________________________________________________________________________________
## 📖 About this experience
During this workshop, we worked in teams to:

  - Learn what a CanSat is and how it relates to CubeSat education.
  - Explore satellite subsystems (OBC, power, ADCS, payload, communication).
  - Get hands-on with ESP32 microcontrollers and Arduino IDE.
  - Connect and program sensors:
    - BMP180 (barometer – pressure, altitude, temperature)
    - MPU6050 (accelerometer & gyroscope)
    - HMC5883L (magnetometer / compass)
    - GPS NEO-6M (position tracking)
  - Log data on SD cards.
  - Use a buzzer beacon for recovery after landing.
  - Build and test a ground station for receiving telemetry.
  - Integrate a camera (ESP32-CAM).
  - Assemble all components onto a prototype board.
  - Prepare mass budgets, flight readiness, and collect/analyze flight data.
  <img src="https://github.com/user-attachments/assets/d5da06c4-124e-4cce-a026-e11a74a112bc" width="400" />
  
  ________________________________________________________________________________________________
  
## 🛰️ What I Learned

As a participant, I learned:

  - How to wire and integrate multiple satellite subsystems.
  - How to program an ESP32 using Arduino IDE.
  - Basics of telemetry and ground station communication.
  - How to collect, store, and visualize sensor data from flight tests.
  - The importance of teamwork in satellite development.

<img src="https://github.com/user-attachments/assets/c726b3de-5a1b-443d-aec7-479b7115c94d" width="300" />

  ________________________________________________________________________________________________
  
## 📡 Ground Station GUI

We developed an enhanced ground station interface named "SatRiders CanSat Ground Station" for the event. This GUI provides real-time telemetry visualization and mission control capabilities:


![1758032374638 (1)](https://github.com/user-attachments/assets/c9e34ecc-28ec-49b0-8b17-e617f4f71398)

Key features of our ground station interface:

  - **Mission Status Monitoring:** Real-time tracking of launch phase, flight time, and event logging
  - **Telemetry Visualization:** Multiple data panels displaying:
    - Altitude and vertical velocity
    - Temperature readings
    - GPS location with map integration
    - Barometric pressure
    - 3D acceleration
  - **System Status Indicators:** Signal strength, descent rate, and packet reception monitoring
  - **Data Recording:** CSV logging with timestamp functionality
  - **Real-time Graphing:** Visual plots of altitude, pressure, temperature, velocity, and acceleration
  - **GPS Tracking:** Map-based position visualization using OpenStreetMap integration
The ground station establishes communication with the CanSat through wireless telemetry, providing comprehensive flight data monitoring and analysis capabilities.
________________________________________________________________________________________________

## 📂 Repository Purpose

This repo is a personal archive of my participation. It contains:

  - 📑 Workshop materials and documentation (docs/)
  - 💻 CanSat firmware and Arduino code (Firmware/)  
  - 🖥️ Ground station graphical user interface (GUI/)
  - 📸 Project photos and diagrams (Images/)
________________________________________________________________________________________________

## 📂 Structure


```bash
📦 International-CanSat-Training-Workshop-Aerospace-Symposium/
├── README.md              # This file
├── docs/                  # Workshop materials, guides, and documentation
├── Firmware/              # Arduino/ESP32 code for the CanSat
├── GUI/                   # Ground station interface for telemetry visualization
├── Images/                # Project photos, diagrams, and screenshots
```

________________________________________________________________________________________________

## 📂 Results

  - Received a shield award for successful launch and operation.
  - Launched and recovered a fully functional CanSat.
  - Improved skills in embedded systems and telemetry.

<img width="331" height="184" alt="image" src="https://github.com/user-attachments/assets/7fc0aa6e-760b-498e-b380-828715a743bc" />  <img width="210" height="164" alt="image" src="https://github.com/user-attachments/assets/973b92a3-02b8-4dd0-9ffa-1f226b0167f5" />  <img width="165" height="179" alt="image" src="https://github.com/user-attachments/assets/96f05f02-3249-44ea-889d-978529a95201" />   <img width="161" height="179" alt="image" src="https://github.com/user-attachments/assets/49112410-617a-46c8-a185-59e41d079022" />

________________________________________________________________________________________________

## 📡 Launch Video 




https://github.com/user-attachments/assets/3d17ab99-5851-401a-bf07-18f1ec8423b9





