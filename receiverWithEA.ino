#include <SPI.h>
#include <RH_RF95.h>
#include <Crypto.h>
#include <SHA256.h>
#include <HMAC.h>

// Singleton instance of radio driver
RH_RF95 rf95;
int led = 13;   // Define LED pin for activity indication

// Message fields
int SEQ;
int TAGID;
int TTL;
int thisRSSI;
int RELAYID = 1;         // Identity of Relay (can be read from SD card)
int RELAY;
int TYPE = 1;            // Message type
char USER_ID[20];        // User ID field
char CUSTOM_MESSAGE[80]; // Custom message field

int MESSAGELENGTH = 100; // Maximum message length
double CSMATIME = 10;    // Check channel status interval (in ms)

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
  pinMode(led, OUTPUT);
  Serial.begin(9600);
  Serial.println("Receiver Version 1");

  while (!Serial)
    Serial.println("Waiting for serial port");

  while (!rf95.init()) {
    Serial.println("Initialization of LoRa receiver failed");
    delay(1000);
  }

  rf95.setFrequency(868.0);  // Set frequency to 868 MHz
  rf95.setTxPower(23, false);// Set transmit power to 23 dBm
  rf95.setSignalBandwidth(500000);  // Set signal bandwidth
  rf95.setSpreadingFactor(12);      // Set spreading factor
}

void loop() {
  uint8_t buf[MESSAGELENGTH];
  uint8_t len = sizeof(buf);

  // Check for user input to send a reply
  if (Serial.available() > 0) {
    // Read the custom message from the serial monitor
    int len = Serial.readBytesUntil('\n', CUSTOM_MESSAGE, sizeof(CUSTOM_MESSAGE) - 1);
    CUSTOM_MESSAGE[len] = '\0';  // Null-terminate the string

    // Clear input buffer
    while (Serial.available() > 0) {
      Serial.read();
    }

    // Prepare and send the reply message
    SEQ++;
    char reply[MESSAGELENGTH];
    char sender[20] = "Ann";  // Receiver's username
    sprintf(reply, "%5d %5d %5d %5d %5d %5d %s %s", SEQ, TYPE, TAGID, RELAYID, TTL, thisRSSI, sender, CUSTOM_MESSAGE);
    for (int i = 0; i < MESSAGELENGTH; i++)
      buf[i] = reply[i];

    rf95.setModeIdle();  // Some obscure bug causing loss of every second message

    // Channel should be idle but if not wait for it to go idle
    while (rf95.isChannelActive()) {
      delay(CSMATIME);  // Wait for channel to go idle by checking frequently
      Serial.println("Receiver node
      node looping on isChannelActive()");  // DEBUG
    }

    // Encrypt the reply message
    xorCipher(buf, sizeof(buf), key, sizeof(key));

    // Generate MAC on the encrypted message
    uint8_t mac[32]; // SHA256 output size
    generateMAC(buf, sizeof(buf), mac, sizeof(mac));

    // Append MAC to message
    memcpy(buf + sizeof(buf) - sizeof(mac), mac, sizeof(mac));

    // Transmit reply message
    Serial.print("Transmitted reply: ");  // DEBUG
    Serial.println((char *)buf);  // DEBUG
    rf95.send(buf, sizeof(buf));
    rf95.waitPacketSent();
  }

  if (rf95.available()) {
    // If a message is available
    if (rf95.recv(buf, &len)) {
      digitalWrite(led, HIGH);  // Indicate message reception

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

        // Unpack the message
        char str[MESSAGELENGTH + 1];
        for (int i = 0; i < MESSAGELENGTH; i++)
          str[i] = buf[i];
        str[MESSAGELENGTH] = '\0';  // Null-terminate the string

        // Extract subfields using sscanf
        sscanf(str, "%5d %5d %5d %5d %5d %5d %s %s", &SEQ, &TYPE, &TAGID, &RELAY, &TTL, &thisRSSI, USER_ID, CUSTOM_MESSAGE);

        // Display the received message details
        Serial.print("Received Seq "); Serial.print(SEQ);
        Serial.print(" Type "); Serial.print(TYPE);
        Serial.print(" Tag "); Serial.print(TAGID);
        Serial.print(" Relay "); Serial.print(RELAY);
        Serial.print(" TTL "); Serial.print(TTL);
        Serial.print(" RSSI "); Serial.print(thisRSSI);
        Serial.print(" User "); Serial.print(USER_ID);
        Serial.print(" Custom Message: "); Serial.print(CUSTOM_MESSAGE);  // Display custom message
        Serial.println(" ");
      } else {
        Serial.println("MAC verification failed!");
      }

      digitalWrite(led, LOW);  // Turn off the LED
    }
  }
}
