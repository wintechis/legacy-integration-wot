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


#define NUM_SERVICE_CAPABILITIES    70 // 1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100
// Define Service UUIDs as Macros
struct BLEPair {
    const char* serviceUUID;
    const char* characteristicUUID;
};

// Array of standard Service UUID and Characteristic UUID combinations
const BLEPair standardPairs[] = {
    // Generic Access Profile
    {"1800", "2A00"}, // Device Name
    {"1800", "2A01"}, // Appearance
    {"1800", "2A04"}, // Peripheral Preferred Connection Parameters
    
    // Generic Attribute Profile
    {"1801", "2A05"}, // Service Changed
    
    // Device Information
    {"180A", "2A23"}, // System ID
    {"180A", "2A24"}, // Model Number String
    {"180A", "2A25"}, // Serial Number String
    {"180A", "2A26"}, // Firmware Revision String
    {"180A", "2A27"}, // Hardware Revision String
    {"180A", "2A28"}, // Software Revision String
    {"180A", "2A29"}, // Manufacturer Name String
    {"180A", "2A2A"}, // IEEE 11073-20601 Regulatory Certification Data List
    {"180A", "2A50"}, // PnP ID
    
    // Battery Service
    {"180F", "2A19"}, // Battery Level
    
    // Heart Rate Service
    {"180D", "2A37"}, // Heart Rate Measurement
    {"180D", "2A38"}, // Body Sensor Location
    {"180D", "2A39"}, // Heart Rate Control Point
    
    // Health Thermometer
    {"1809", "2A1C"}, // Temperature Measurement
    {"1809", "2A1D"}, // Temperature Type
    {"1809", "2A1E"}, // Intermediate Temperature
    
    // Blood Pressure
    {"1810", "2A35"}, // Blood Pressure Measurement
    {"1810", "2A36"}, // Intermediate Cuff Pressure
    {"1810", "2A49"}, // Blood Pressure Feature
    
    // User Data
    {"181C", "2A8A"}, // First Name
    {"181C", "2A90"}, // Last Name
    {"181C", "2A98"}, // Weight
    {"181C", "2A9D"}, // Height
    {"181C", "2A9E"}, // BMI
    {"181C", "2A9F"}, // Age
    
    // Running Speed and Cadence
    {"1814", "2A53"}, // RSC Measurement
    {"1814", "2A54"}, // RSC Feature
    {"1814", "2A55"}, // SC Control Point
    
    // Cycling Speed and Cadence
    {"1816", "2A5B"}, // CSC Measurement
    {"1816", "2A5C"}, // CSC Feature
    {"1816", "2A5D"}, // Sensor Location
    {"1816", "2A55"}, // SC Control Point
    
    // Cycling Power
    {"1818", "2A63"}, // Cycling Power Measurement
    {"1818", "2A65"}, // Cycling Power Feature
    {"1818", "2A66"}, // Cycling Power Control Point
    
    // Location and Navigation
    {"1819", "2A67"}, // Location and Speed
    {"1819", "2A68"}, // Navigation
    {"1819", "2A69"}, // Position Quality
    {"1819", "2A6A"}, // LN Feature
    {"1819", "2A6B"}, // LN Control Point
    
    // Environmental Sensing
    {"181A", "2A6E"}, // Temperature
    {"181A", "2A6F"}, // Humidity
    {"181A", "2A70"}, // Pressure
    
    // Body Composition
    {"181B", "2A9B"}, // Body Composition Measurement
    {"181B", "2A9C"}, // Body Composition Feature
    
    // Weight Scale
    {"181D", "2A9E"}, // Weight Measurement
    {"181D", "2A9F"}, // Weight Scale Feature
    
    // Bond Management
    {"181E", "2AA4"}, // Bond Management Control Point
    {"181E", "2AA5"}, // Bond Management Feature
    
    // Continuous Glucose Monitoring
    {"181F", "2AA7"}, // CGM Measurement
    {"181F", "2AA8"}, // CGM Feature
    {"181F", "2AA9"}, // CGM Status
    {"181F", "2AAA"}, // CGM Session Start Time
    {"181F", "2AAB"}, // CGM Session Run Time
    {"181F", "2AAC"}, // CGM Specific Ops Control Point
    
    // Internet Protocol Support
    {"1820", "2AAE"}, // IP Support Configuration
    
    // Indoor Positioning
    {"1821", "2AAD"}, // Indoor Positioning Configuration
    {"1821", "2AAF"}, // Latitude
    {"1821", "2AB0"}, // Longitude
    {"1821", "2AB1"}, // Local North Coordinate
    {"1821", "2AB2"}, // Local East Coordinate
    
    // Pulse Oximeter
    {"1822", "2A5E"}, // PLX Spot-Check Measurement
    {"1822", "2A5F"}, // PLX Continuous Measurement
    
    // HTTP Proxy
    {"1823", "2ABD"}, // HTTP Control Point
    {"1823", "2ABE"}, // HTTP Status Code
    
    // Transport Discovery
    {"1824", "2ABF"}, // Transport Discovery Data
    
    // Object Transfer
    {"1825", "2AC5"}, // Object Transfer Control Point
    {"1825", "2AC8"}, // Object Name
    
    // Fitness Machine
    {"1826", "2ACC"}, // Fitness Machine Feature
    {"1826", "2ACD"}, // Treadmill Data
    {"1826", "2ACE"}, // Cross Trainer Data
    {"1826", "2ACF"}, // Step Climber Data
    
    // Mesh Provisioning
    {"1827", "2ADB"}, // Mesh Provisioning Data In
    {"1827", "2ADC"}, // Mesh Provisioning Data Out
    
    // Mesh Proxy
    {"1828", "2ADD"}, // Mesh Proxy Data In
    {"1828", "2ADE"}, // Mesh Proxy Data Out
    
    // Audio Input Control
    {"1843", "2B77"}, // Audio Input State
    {"1843", "2B78"}, // Gain Settings Attribute
    {"1843", "2B79"}, // Audio Input Type
    {"1843", "2B7A"}, // Audio Input Status
    
    // Volume Control
    {"1844", "2B7D"}, // Volume State
    {"1844", "2B7E"}, // Volume Control Point
    {"1844", "2B7F"}, // Volume Flags
    
    // Audio Output Control
    {"1845", "2B83"}, // Audio Output State
    {"1845", "2B84"}, // Audio Output Description
    
    // Microphone Control
    {"1846", "2B88"}, // Microphone Control Point
    {"1846", "2B89"}, // Microphone State
    
    // Constant Tone Extension
    {"1853", "2BAA"}, // CTE Enable
    {"1853", "2BAB"}, // CTE Minimum Length
    
    // Telephone Bearer
    {"1855", "2BB9"}, // Bearer Technology
    {"1855", "2BBA"}, // Bearer Signal Strength
    {"1855", "2BBB"}, // Bearer Signal Strength Reporting Interval
    {"1855", "2BBC"}, // Bearer List Current Calls
    
    // Generic Media Control
    {"1856", "2BC0"}, // Media Player Name
    {"1856", "2BC1"}, // Media Player Icon Object ID
    {"1856", "2BC2"}, // Media Player Icon URL
    {"1856", "2BC3"}, // Track Changed
    {"1856", "2BC4"}, // Track Title
    {"1856", "2BC5"}, // Track Duration
    {"1856", "2BC6"}, // Track Position
    
    // Generic Telephone Bearer
    {"1857", "2BCD"}, // Bearer Signal Strength
    {"1857", "2BCE"}, // Bearer Signal Strength Reporting Interval
    
    // Binary Sensor
    {"183B", "2B2B"}, // Binary Sensor State
    {"183B", "2B2C"}, // Binary Sensor State Characteristic Descriptor
};

const int totalPairs = sizeof(standardPairs) / sizeof(standardPairs[0]);


// Function to get n number of unique Service-Characteristic pairs
void getServiceCharacteristicPairs(int n, BLEPair* result) {
    if (n > totalPairs) {
        n = totalPairs;  // Limit to available pairs
    }

    // Use Fisher-Yates shuffle algorithm to get random unique pairs
    BLEPair tempArray[totalPairs];
    memcpy(tempArray, standardPairs, sizeof(standardPairs));

    for (int i = totalPairs - 1; i > 0; i--) {
        int j = random(i + 1);
        BLEPair temp = tempArray[i];
        tempArray[i] = tempArray[j];
        tempArray[j] = temp;
    }

    // Copy the first n pairs to the result array
    memcpy(result, tempArray, n * sizeof(BLEPair));
}



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

    BLEPair selectedPairs[NUM_SERVICE_CAPABILITIES];
    getServiceCharacteristicPairs(NUM_SERVICE_CAPABILITIES, selectedPairs);

    for (int i = 0; i < NUM_SERVICE_CAPABILITIES; i++) {
        BLEService *pService = pServer->createService(selectedPairs[i].serviceUUID);
        BLECharacteristic *pCharacteristic = pService->createCharacteristic(
            selectedPairs[i].characteristicUUID,
            NIMBLE_PROPERTY::READ | NIMBLE_PROPERTY::WRITE
        );
        pCharacteristic->setValue("Default Value");
        pService->start();
    }


  
  // BLEAdvertising *pAdvertising = pServer->getAdvertising();  // this still is working for backward compatibility
  // Start advertising
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->start();

  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);  // functions that help with iPhone connections issue
  pAdvertising->setMaxPreferred(0x12);

  BLEDevice::startAdvertising();
  Serial.println("Characteristic defined! Now you can read it in your phone!");
  Serial.print("Number of services: ");
  Serial.println(NUM_SERVICE_CAPABILITIES);
}

void loop() {
  // put your main code here, to run repeatedly:
  delay(2000);
}