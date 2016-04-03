 /*
* Relay driver for controlling an antenna switch
*
* Antenna(s) to rig(s) switching is controlled by UDP commands from a client.
*
* Hardware used:
*  Arduino MEGA
*  Arduino Ethernet Shield
*  8 Relay Module
*  TBD VSWR bridge - SOTABEAMS BOXA-SWR High Performance VSWR Bridge                        
*/

//////////////////////////////////////////////////////////////////////////
// UDP section
#include <SPI.h>                  // Needed for Arduino versions later than 0018
#include <Ethernet.h>
#include <EthernetUdp.h>         // UDP library from: bjoern@cs.stanford.edu 12/30/2008

// Specify MAC and IP address:
byte mac[] = {
  0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xEF
  //0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED
};
IPAddress ip(192, 168, 1, 177);
// Local port to listen on
unsigned int localPort = 8888;

// Buffers for receiving and sending data
char packetBuffer[UDP_TX_PACKET_MAX_SIZE]; // Buffer to hold incoming packet,
char  ReplyBuffer[128];                   // The response
char  StatusBuffer[128];                  // Interim data

// An EthernetUDP instance to let us send and receive packets over UDP
EthernetUDP Udp;

//////////////////////////////////////////////////////////////////////////
// Relay section
// Pin allocation
const int relay_base = 1;
const int relay_1 = 2;
const int relay_2 = 3;
const int relay_3 = 4;
const int relay_4 = 5;
const int relay_5 = 6;
const int relay_6 = 7;
const int relay_7 = 8;
const int relay_8 = 9;

//////////////////////////////////////////////////////////////////////////
// SWR meter section
// Pin allocation
const int fwdPin = 0;
const int refPin = 1;

//////////////////////////////////////////////////////////////////////////
void setup() {
  
  // Start Ethernet and UDP:
  Ethernet.begin(mac, ip);
  Udp.begin(localPort);
  
  // Configure the pins used to drive the relays
  pinMode(relay_1, OUTPUT);
  pinMode(relay_2, OUTPUT);
  pinMode(relay_3, OUTPUT);
  pinMode(relay_4, OUTPUT);
  pinMode(relay_5, OUTPUT);
  pinMode(relay_6, OUTPUT);
  pinMode(relay_7, OUTPUT);
  pinMode(relay_8, OUTPUT);
  // Relays are active LOW so ensure all are de-energised
  reset_relays();

  // Initialise serial port to be used for debug
  Serial.begin(9600);
}

//////////////////////////////////////////////////////////////////////////
void loop() {
  // Called to execute main code
  // Accept messages from UDP
  int packetSize = queryPacket();
  // If there's data available, read a packet
  if (packetSize) {
    // Read and reply
    doRead(packetSize);   
    // Execute command
    execute(packetBuffer);
    // Send response
    sendResponse();
  }
  delay(10);
}

//////////////////////////////////////////////////////////////////////////
int queryPacket() {
  
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    return packetSize;
  }
   else
     return 0;
}

//////////////////////////////////////////////////////////////////////////
int doRead(int packetSize) {
  
  // Read the packet into packetBufffer
  Udp.read(packetBuffer, UDP_TX_PACKET_MAX_SIZE);
  // Terminate buffer
  packetBuffer[packetSize] = '\0';
  //Serial.println("Command:");
  //Serial.println(packetBuffer); 
}

//////////////////////////////////////////////////////////////////////////
int sendResponse() {

  // Send a reply to the IP address and port that sent us the packet we received
  Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
  Udp.write(ReplyBuffer);
  Udp.endPacket();   
}

//////////////////////////////////////////////////////////////////////////
int sendVSWR(int forward, int reflected) {

  // Send a VSWR report to the IP address and port that sent us the packet we received
  strcpy(StatusBuffer, "vswr:");
  sprintf(StatusBuffer + strlen(StatusBuffer), "%d", forward);
  strcpy(StatusBuffer + strlen(StatusBuffer), ":");
  sprintf(StatusBuffer + strlen(StatusBuffer), "%d", reflected);
  Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());    
  Udp.write(StatusBuffer);
  Udp.endPacket();  
}

//////////////////////////////////////////////////////////////////////////
void execute(char *command) {
  
  /*
  * The command set is as follows. Commands are terminated strings.
  * Ping        - "ping"      -  connectivity test
  * Relay reset - "reset"     -  de-energise all relays
  * Relay on    - "[1-8]e"    -  energise relay 1-8
  * Relay off   - "[1-8]d"    -  de-energise relay 1-8
  */ 
    
  char *p;
  int value = 0;
  bool valid = false;
  
  // Assume success
  strcpy(ReplyBuffer, "success");
  if (strcmp(command, "ping") == 0) {
    valid = true;
  } else if (strcmp(command, "reset") == 0) {
    reset_relays();
    valid = true;
  } else {
    // A numeric command
    for(p=command; *p; p++) {
     if(*p >= '0' && *p <= '9') {
        // Numeric entered, so accumulate numeric value
        value = value*10 + *p - '0';
     } else if(*p == 'e') {
        energise_relay(value);
        valid = true;
     } else if(*p == 'd') {
        de_energise_relay(value);
        valid = true;
     }
    }
  }
  if (!valid) {
    // Invalid command
    Serial.println("failure:Invalid command:");
    Serial.println(command);
    strcpy(ReplyBuffer, "failure:Invalid command");
  }
}

//////////////////////////////////////////////////////////////////////////
void reset_relays() {
  
  digitalWrite(relay_1, HIGH);
  digitalWrite(relay_2, HIGH);
  digitalWrite(relay_3, HIGH);
  digitalWrite(relay_4, HIGH);
  digitalWrite(relay_5, HIGH);
  digitalWrite(relay_6, HIGH);
  digitalWrite(relay_7, HIGH);
  digitalWrite(relay_8, HIGH);
}

//////////////////////////////////////////////////////////////////////////
void energise_relay(int relay_id) {
  
  digitalWrite(relay_id + relay_base, LOW);
}

//////////////////////////////////////////////////////////////////////////
void de_energise_relay(int relay_id) {
  
  digitalWrite(relay_id + relay_base, HIGH);
}
  

