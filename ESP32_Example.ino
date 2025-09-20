/*
 * ESP32 Example Code for AI-Enhanced Career Guidance System
 * This code demonstrates how to connect ESP32 to the MQTT broker
 * and send focus monitoring data.
 * 
 * Hardware Requirements:
 * - ESP32 development board
 * - Button or sensor for focus detection
 * - WiFi connection
 * 
 * Libraries Required:
 * - WiFi.h (built-in)
 * - PubSubClient.h (install via Library Manager)
 * - ArduinoJson.h (install via Library Manager)
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// WiFi Configuration
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// MQTT Configuration
const char* mqtt_server = "YOUR_BROKER_IP";  // Change to your MQTT broker IP
const int mqtt_port = 1883;
const char* mqtt_user = "";  // Leave empty if no authentication
const char* mqtt_password = "";  // Leave empty if no authentication

// User Configuration
const int USER_ID = 1;  // Change this to match the user ID

// Pin Configuration
const int FOCUS_BUTTON_PIN = 2;  // Button to indicate focus status
const int LED_PIN = 4;  // LED to show connection status

// MQTT Topics
const char* focus_topic = "monitor/1/focus";  // Update with actual user ID
const char* metadata_topic = "monitor/1/metadata";  // Update with actual user ID

// Global Variables
WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
bool lastFocusState = false;
bool currentFocusState = false;
unsigned long focusStartTime = 0;
unsigned long sessionDuration = 0;

void setup() {
  Serial.begin(115200);
  
  // Initialize pins
  pinMode(FOCUS_BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  
  // Connect to WiFi
  setup_wifi();
  
  // Setup MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  
  Serial.println("ESP32 Career Guidance Monitor Started");
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str(), mqtt_user, mqtt_password)) {
      Serial.println("connected");
      digitalWrite(LED_PIN, HIGH);
      
      // Subscribe to any topics if needed
      // client.subscribe("monitor/1/commands");
      
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      digitalWrite(LED_PIN, LOW);
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Read focus button state
  currentFocusState = !digitalRead(FOCUS_BUTTON_PIN);  // Inverted because of INPUT_PULLUP
  
  // Check if focus state changed
  if (currentFocusState != lastFocusState) {
    lastFocusState = currentFocusState;
    
    if (currentFocusState) {
      // Started focusing
      focusStartTime = millis();
      Serial.println("🎯 Focus started");
    } else {
      // Stopped focusing
      sessionDuration = millis() - focusStartTime;
      Serial.println("😴 Focus ended");
    }
    
    // Publish focus status
    publishFocusStatus(currentFocusState);
  }
  
  // Publish periodic updates while focused
  if (currentFocusState && millis() - lastMsg > 30000) {  // Every 30 seconds
    publishFocusStatus(true);
    lastMsg = millis();
  }
  
  // Publish metadata every minute
  if (millis() - lastMsg > 60000) {  // Every minute
    publishMetadata();
    lastMsg = millis();
  }
  
  delay(100);  // Small delay to prevent overwhelming the system
}

void publishFocusStatus(bool isFocused) {
  String payload = isFocused ? "true" : "false";
  
  if (client.publish(focus_topic, payload.c_str())) {
    Serial.print("📤 Published focus status: ");
    Serial.println(payload);
  } else {
    Serial.println("❌ Failed to publish focus status");
  }
}

void publishMetadata() {
  // Create JSON metadata
  StaticJsonDocument<200> doc;
  doc["timestamp"] = millis();
  doc["user_id"] = USER_ID;
  doc["focus_status"] = currentFocusState ? "focused" : "distracted";
  doc["session_duration"] = currentFocusState ? (millis() - focusStartTime) : sessionDuration;
  doc["wifi_rssi"] = WiFi.RSSI();
  doc["free_heap"] = ESP.getFreeHeap();
  
  String metadata;
  serializeJson(doc, metadata);
  
  if (client.publish(metadata_topic, metadata.c_str())) {
    Serial.print("📊 Published metadata: ");
    Serial.println(metadata);
  } else {
    Serial.println("❌ Failed to publish metadata");
  }
}

/*
 * Additional Functions for Advanced Features
 */

void publishHeartbeat() {
  // Send heartbeat to indicate device is alive
  String heartbeat_topic = "monitor/1/heartbeat";
  String payload = "{\"status\":\"alive\",\"timestamp\":" + String(millis()) + "}";
  
  if (client.publish(heartbeat_topic, payload.c_str())) {
    Serial.println("💓 Heartbeat sent");
  }
}

void publishError(String error) {
  // Publish error messages
  String error_topic = "monitor/1/error";
  String payload = "{\"error\":\"" + error + "\",\"timestamp\":" + String(millis()) + "}";
  
  client.publish(error_topic, payload.c_str());
  Serial.println("❌ Error published: " + error);
}

/*
 * Configuration Instructions:
 * 
 * 1. Update WiFi credentials:
 *    - Change ssid and password to your WiFi network
 * 
 * 2. Update MQTT broker settings:
 *    - Change mqtt_server to your broker IP address
 *    - Update mqtt_user and mqtt_password if authentication is required
 * 
 * 3. Update user ID:
 *    - Change USER_ID to match the user in your system
 *    - Update focus_topic and metadata_topic accordingly
 * 
 * 4. Hardware connections:
 *    - Connect a button between pin 2 and GND (with pull-up resistor)
 *    - Connect an LED between pin 4 and GND (with current limiting resistor)
 * 
 * 5. Upload and monitor:
 *    - Upload this code to your ESP32
 *    - Open Serial Monitor to see debug messages
 *    - Press the button to simulate focus/study sessions
 * 
 * 6. Test MQTT:
 *    - Use MQTT client tools to subscribe to monitor/1/focus
 *    - Verify messages are being received
 */
