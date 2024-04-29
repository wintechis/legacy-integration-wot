/*
    Based on Neil Kolban example for IDF: https://github.com/nkolban/esp32-snippets/blob/master/cpp_utils/tests/BLE%20Tests/SampleServer.cpp
    Ported to Arduino ESP32 by Evandro Copercini
    updates by chegewara
*/

/** NimBLE differences highlighted in comment blocks **/

/*******original********
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
***********************/

#include <NimBLEDevice.h>


// Defines the number of services to be created
#define NUM_SERVICE_CAPABILITIES    100 // 1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100

// Define Service UUIDs as Macros
#define SERVICE_UUID_TIME           "00001805-0000-1000-8000-00805f9b34fb"
#define SERVICE_UUID_GLUCOSE        "00001808-0000-1000-8000-00805f9b34fb"
#define SERVICE_UUID_HEALTH_THERMO  "00001809-0000-1000-8000-00805f9b34fb"
#define SERVICE_UUID_PHONE_ALERT    "0000180e-0000-1000-8000-00805f9b34fb"
#define SERVICE_UUID_HEART_RATE     "0000180d-0000-1000-8000-00805f9b34fb"
#define SERVICE_UUID_BLOOD_PRESSURE "00001810-0000-1000-8000-00805f9b34fb"
#define SERVICE_UUID_RUNNING_SPEED  "00001814-0000-1000-8000-00805f9b34fb"
#define SERVICE_UUID_CYCLING_SPEED  "00001815-0000-1000-8000-00805f9b34fb"
#define SERVICE_UUID_BATTERY        "0000180f-0000-1000-8000-00805f9b34fb"
#define SERVICE_UUID_RANDOM         "4fafc201-1fb5-459e-8fcc-c5c9c331914b"

// Define Characteristic UUIDs as Macros
#define CHAR_UUID_TIME_CURRENT      "00002a2b-0000-1000-8000-00805f9b34fb"
#define CHAR_UUID_HEALTH_TEMP_MEAS  "00002a1c-0000-1000-8000-00805f9b34fb"
#define CHAR_UUID_HEALTH_TEMP_TYPE  "00002a1d-0000-1000-8000-00805f9b34fb"
#define CHAR_UUID_HEALTH_TEMP_INTER "00002a1e-0000-1000-8000-00805f9b34fb"
#define CHAR_UUID_HEART_RATE_MEAS   "00002a37-0000-1000-8000-00805f9b34fb"
#define CHAR_UUID_BATTERY_LEVEL     "00002a19-0000-1000-8000-00805f9b34fb"
#define CHAR_UUID_GLUCOSE_FEATURE   "00002a51-0000-1000-8000-00805f9b34fb"
#define CHAR_UUID_BODY_LOCATION     "00002a38-0000-1000-8000-00805f9b34fb"
#define CHAR_UUID_ALERT_STATUS      "00002a3f-0000-1000-8000-00805f9b34fb"
#define CHAR_UUID_RANDOM            "beb5483e-36e1-4688-b7f5-ea07361b26a8"

// Arrays to store UUIDs
const char* serviceUUIDs[] = {
    SERVICE_UUID_TIME,
    SERVICE_UUID_GLUCOSE,
    SERVICE_UUID_PHONE_ALERT,
    SERVICE_UUID_HEALTH_THERMO,
    SERVICE_UUID_HEART_RATE,
    SERVICE_UUID_BLOOD_PRESSURE,
    SERVICE_UUID_RUNNING_SPEED,
    SERVICE_UUID_BATTERY,
    SERVICE_UUID_CYCLING_SPEED,
    SERVICE_UUID_RANDOM
};

const char* characteristicUUIDs[] = {
    CHAR_UUID_TIME_CURRENT,
    CHAR_UUID_HEALTH_TEMP_MEAS,
    CHAR_UUID_HEALTH_TEMP_TYPE,
    CHAR_UUID_HEALTH_TEMP_INTER,
    CHAR_UUID_HEART_RATE_MEAS,
    CHAR_UUID_BATTERY_LEVEL,
    CHAR_UUID_GLUCOSE_FEATURE,
    CHAR_UUID_BODY_LOCATION,
    CHAR_UUID_ALERT_STATUS,
    CHAR_UUID_RANDOM
};

void setup() {
  Serial.begin(115200);
  Serial.println("Starting BLE work!");

  BLEDevice::init("MyTestDevice");

  /** Optional: set the transmit power, default is 3db */
#ifdef ESP_PLATFORM
  NimBLEDevice::setPower(ESP_PWR_LVL_P9); /** +9db */
#else
  NimBLEDevice::setPower(9); /** +9db */
#endif
  BLEServer *pServer = BLEDevice::createServer();

  int counter = 0;
  for (int i = 0; i < sizeof(serviceUUIDs) / sizeof(serviceUUIDs[0]); i++) {
        if (counter > NUM_SERVICE_CAPABILITIES){
            Serial.println("Enough services");
            Serial.print("Number of services");
            Serial.println(counter);
            break;
          }
        BLEService *pService = pServer->createService(serviceUUIDs[i]);
        for (int j = 0; j < sizeof(characteristicUUIDs) / sizeof(characteristicUUIDs[0]); j++) {
          if (counter > NUM_SERVICE_CAPABILITIES){
            Serial.println("Enough services");
            break;
          }
          
          BLECharacteristic *pCharacteristic = pService->createCharacteristic(
                                                characteristicUUIDs[j],
                                                NIMBLE_PROPERTY::READ |
                                                NIMBLE_PROPERTY::WRITE 
                                              );
        
          pCharacteristic->setValue("Hello World says Neil");
          counter++;
        }
        pService->start();
    
  }


  
  // BLEAdvertising *pAdvertising = pServer->getAdvertising();  // this still is working for backward compatibility
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  for (int i = 0; i < sizeof(serviceUUIDs) / sizeof(serviceUUIDs[0]); i++) {
      pAdvertising->addServiceUUID(SERVICE_UUID_RANDOM);
  }

  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);  // functions that help with iPhone connections issue
  pAdvertising->setMaxPreferred(0x12);

  BLEDevice::startAdvertising();
  Serial.println("Characteristic defined! Now you can read it in your phone!");
  Serial.print("Number of services: ");
  Serial.println(counter - 1);
}

void loop() {
  // put your main code here, to run repeatedly:
  delay(2000);
}
