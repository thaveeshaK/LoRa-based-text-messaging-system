#include <SPI.h>
#include <RH_RF95.h>

// Singleton instance of the radio driver
RH_RF95 rf95;

const int led = 13; // Define LED pin for activity indication

void setup() {
  // Initialize LoRa transceiver
  pinMode(led, OUTPUT);
  Serial.begin(9600);
  while (!Serial) {
    delay(100);
  }

  if (!rf95.init()) {
    Serial.println("Initialisation of LoRa receiver failed");
    while (1) {
      delay(1000); // Wait here forever
    }
  }

  rf95.setFrequency(915.0);   // Set to use 915 MHz
  rf95.setTxPower(5, false);
  rf95.setSignalBandwidth(500000);
  rf95.setSpreadingFactor(12);
}

void loop() {
  // Read input from serial monitor and send via LoRa
  if (Serial.available()) {
    String customMessage = Serial.readStringUntil('\n');
    uint8_t buf[customMessage.length() + 1];
    customMessage.getBytes(buf, customMessage.length() + 1);
    rf95.send(buf, customMessage.length() + 1);
    rf95.waitPacketSent();
    Serial.print("Transmitted message: ");
    Serial.println(customMessage); // Print the message sent by Host A
  }

  // Check if a message is available from the LoRa receiver
  if (rf95.available()) {
    uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
    uint8_t len = sizeof(buf);
    if (rf95.recv(buf, &len)) {
      digitalWrite(led, HIGH); // Turn on LED to indicate activity
      Serial.print("Received message from Host B: ");
      Serial.println((char*)buf); // Print the received message
      digitalWrite(led, LOW); // Turn off LED
    } else {
      Serial.println("recv failed");
    }
  }
}
