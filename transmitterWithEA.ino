#include <SPI.h>
#include <RH_RF95.h>
#include <Crypto.h>
#include <SHA256.h>
#include <HMAC.h>

// Singleton instance of radio driver
RH_RF95 rf95;
int led = 13;   // Define LED pin in case we want to use it to demonstrate activity

// Message fields
int SEQ = 0;     // Sequence number
int TYPE = 0;    // Message type
int TAGID = 1;   // Identity of tag. Will eventually be read from an SD card.
int RELAYID = 0;
int TTL = 5;
int thisRSSI = 0;
char USER_ID[20] = "John";  // Sender's username
char CUSTOM_MESSAGE[80];     // Custom message field

int MESSAGELENGTH = 100;
int TXINTERVAL = 5000;  // Time between transmissions (in ms)
double CSMATIME = 10;   // Check the status of the channel every 10 ms

const uint8_t key[] = {0xAA, 0xBB, 0xCC, 0xDD};  // Example key for XOR cipher
const uint8_t hmacKey[] = {0x01, 0x02, 0x03, 0x04};  // Example key for HMAC

void xorCipher(uint8_t *data, size_t length, const uint8_t *key, size_t keyLength) {
  for (size_t i = 0; i < length; i++) {
    data[i] ^= key[i % keyLength];
  }
}

void generateMAC(const uint8_t *message, size_t messageLength, uint8_t *mac, size_t macLength) {
  SHA256 sha256;
  HMAC<SHA256> hmac(hmacKey, sizeof(hmacKey));
  hmac.update(message, messageLength);
  hmac.finalize(mac, macLength);
}

void setup() {
  // Initialise LoRa transceiver
  pinMode(led, OUTPUT);
  Serial.begin(9600);
  Serial.println("Tag version 1");

  if (!rf95.init()) {
    Serial.println("Initialization of LoRa receiver failed");
    while (1); // Halt if LoRa initialization failed
  }

  rf95.setFrequency(868.0);   // Set frequency to 868 MHz
  rf95.setTxPower(5, false);  // Set transmit power to 5 dBm
  rf95.setSignalBandwidth(500000);  // Set signal bandwidth
  rf95.setSpreadingFactor(12);      // Set spreading factor
}

void loop() {
  // Generate message intermittently (10 seconds)
  uint8_t buf[MESSAGELENGTH];
  uint8_t len = sizeof(buf);
  char str[MESSAGELENGTH];

  // Read custom message from serial monitor
  if (Serial.available() > 0) {
    int lenInput = Serial.readBytesUntil('\n', CUSTOM_MESSAGE, sizeof(CUSTOM_MESSAGE) - 1);
    CUSTOM_MESSAGE[lenInput] = '\0';  // Null-terminate the string

    // Prepare message
    SEQ++;
    sprintf(str, "%5d %5d %5d %5d %5d %5d %s %s", SEQ, TYPE, TAGID, RELAYID, TTL, thisRSSI, USER_ID, CUSTOM_MESSAGE);
    for (int i = 0; i < MESSAGELENGTH; i++)
      buf[i] = str[i];

    // Encrypt the message
    xorCipher(buf, sizeof(buf), key, sizeof(key));

    // Generate MAC on the encrypted message
    uint8_t mac[32]; // SHA256 output size
    generateMAC(buf, sizeof(buf), mac, sizeof(mac));

    // Append MAC to message
    memcpy(buf + sizeof(buf) - sizeof(mac), mac, sizeof(mac));

    // Transmit message
    Serial.print("Sending message: ");  // Print the message being sent
    Serial.println((char *)buf);         // Print the message content
    rf95.send(buf, sizeof(buf));
    rf95.waitPacketSent();
    Serial.println("Message sent!");
  }

  // Check for incoming packets
  if (rf95.available()) {
    // Receive incoming packet
    if (rf95.recv(buf, &len)) {
      // Extract MAC from received message
      uint8_t receivedMac[32];
      memcpy(receivedMac, buf + len - sizeof(receivedMac), sizeof(receivedMac));

      // Remove MAC from received message
      memset(buf + len - sizeof(receivedMac), 0, sizeof(receivedMac));

      // Verify MAC on the encrypted message
      uint8_t computedMac[32];
      generateMAC(buf, len - sizeof(receivedMac), computedMac, sizeof(computedMac));

      if (memcmp(receivedMac, computedMac, sizeof(receivedMac)) == 0) {
        // MAC is valid, decrypt and process the message
        xorCipher(buf, len - sizeof(receivedMac), key, sizeof(key));

        Serial.print("Received: ");
        Serial.println((char *)buf);
      } else {
        Serial.println("MAC verification failed!");
      }
    }
  }

  // Wait before sending the next message
  delay(TXINTERVAL);
}
