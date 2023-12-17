//Include the library files
#include <WiFi.h>
#include <LiquidCrystal_I2C.h>
#include <Wire.h>
#include <WiFiClient.h>
#include <ArduinoJson.h>
#include <WebSocketsServer.h>
#include <HTTPClient.h>
#include <PubSubClient.h>
#include "DHTesp.h";
#include "DHT.h";

#define sensor 33
#define relay 4


//Initialize the LCD display
LiquidCrystal_I2C lcd(0x27, 16, 2);

#define DHTPIN 14
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

//Enter your WIFI SSID and password
// char ssid[] = "MinhThu";
// char pass[] = "Khanhhan2017@";
// char ssid[] = "NAM";
// char pass[] = "12345678";
char ssid[] = "Wifichua";
char pass[] = "nha5nguoi";

int interval = 1000;               // virtual delay
unsigned long previousMillis = 0;  // Tracks the time since last event fired

String jsonString;

WiFiClient espClient;
PubSubClient client(espClient);
const char* mqtt_server = "broker.hivemq.com";
const char* mqtt_user="BTL_IOT";
const char* mqtt_password="Btliot123";
unsigned long lastMsg = 0;


float value = 0;

void setup() {
  // Debug console
  Serial.begin(115200);
  Serial.println("started");

  //WIFI
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {  // Check if wifi is connected or not
    delay(500);
    Serial.print("-.-");
  }

  randomSeed(analogRead(A0));

  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  dht.begin();

  client.setServer(mqtt_server, 1883); 
  client.setCallback(callback); 

  lcd.init();
  lcd.backlight();
  pinMode(relay, OUTPUT);
  digitalWrite(relay, HIGH);

  lcd.setCursor(1, 0);
  lcd.print("System Loading");
  for (int a = 0; a <= 15; a++) {
    lcd.setCursor(a, 1);
    lcd.print(".");
    delay(200);
  }
  lcd.clear();
  randomSeed(analogRead(0));
}

void callback(char* topic, byte* payload, unsigned int length) {
  String temp; 
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) { 
    temp += (char)payload[i];
  }

  String subSwitchTopic = "BTL_N26/switch";

  Serial.println(temp.toInt());
  Serial.println(strcmp(topic, subSwitchTopic.c_str()) == 0);

  if (strcmp(topic, subSwitchTopic.c_str()) == 0){
    if (temp.toInt() == 0 ) {
      Serial.print("OFF");
      digitalWrite(relay, HIGH);
      lcd.setCursor(0, 1);
      lcd.print("Motor is OFF");
      // digitalWrite(22, LOW);
    } else {
        Serial.print("ON");
        digitalWrite(relay, LOW);
        lcd.setCursor(0, 1);
        lcd.print("Motor is ON ");
        // digitalWrite(22, HIGH);
    }
  } 
}

void reconnect() { 
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    
    // Attempt to connect
    if (client.connect(clientId.c_str(), mqtt_user, mqtt_password)) {
      Serial.println("Connected to " + clientId);
      client.subscribe("BTL_N26/switch");
      // client.subscribe("BTL_N26/hum");
      // client.subscribe("BTL_N26/soil");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(2000);
    }
  }
}

//Get the ultrasonic sensor values
void soilMoisture() {
  value = analogRead(sensor);
  value = map(value, 0, 4095, 0, 100);
  value = (value - 100) * -1;
  lcd.setCursor(0, 0);
  lcd.print("Moisture :");
  lcd.print(value);
  lcd.print(" ");
}

void loop() {
  lcd.setCursor(1, 0);
  lcd.print("System Loading");

   if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long currentMillis = millis();  // call millis  and Get snapshot of time
  if ((unsigned long)(currentMillis - previousMillis) >= interval) {

    float h = dht.readHumidity();
    float t = dht.readTemperature();
    if(isnan(h)){
      h=0;
    }
    if(isnan(t)){
      t=0;
    }
    String temp = String(t, 2); 
    client.publish("BTL_N26/temp", temp.c_str()); 
    
    String hum = String(h, 2); 
    client.publish("BTL_N26/hum", hum.c_str());

    String soil = String(value); 
    client.publish("BTL_N26/soil", soil.c_str());

    Serial.print("Temperature: ");
    Serial.println(temp);
    Serial.print("Humidity: ");
    Serial.println(hum);
    Serial.print("Soil: ");
    Serial.println(soil);

    soilMoisture();
    previousMillis = currentMillis;  // Use the snapshot to set track time until next event
  }

   delay(1000);
}

