/* Analog Read to LED
 * ------------------ 
 *
 * turns on and off a light emitting diode(LED) connected to digital  
 * pin 13. The amount of time the LED will be on and off depends on
 * the value obtained by analogRead(). In the easiest case we connect
 * a potentiometer to analog pin 2.
 *
 * Created 1 December 2005
 * copyleft 2005 DojoDave <http://www.0j0.org>
 * http://arduino.berlios.de
 *
 */

int potPin = 2;    // select the input pin for the potentiometer
int switchPin = 2; // not analog
int valButton = 0; // variable to store the value of button
int val = 0;       // variable to store the value coming from the sensor
int tempVal = -1;
int serialRate = 9600;
int updateRate = 200;
String return_type = "number";
char byteRead;
void setup() {
  Serial.begin(serialRate);
  // define as switch button
  pinMode(switchPin,INPUT_PULLUP);
  // First Value
  updatePotentiometerValue();
  updateButtonValue();
}

void loop() {
  updatePotentiometerValue();
  updateButtonValue();
  checkRequestAndReturn();
  delay(updateRate);                  // stop the program for some time
}

void updateButtonValue() {
  valButton = digitalRead(switchPin);
}

void checkRequestAndReturn() {
  if (Serial.available()) {
    byteRead = Serial.read();
    if(byteRead == '1') {
      Serial.println(formatReturn(val));
    }else if(byteRead == '2') {
      Serial.println(formatReturn(valButton));
    }
  }
}

void updatePotentiometerValue() {
  val = analogRead(potPin);    // read the value from the sensor
  if(val!=tempVal) {
    tempVal = val;
  }
}

String formatReturn(int returned_val) {
  return String(returned_val);
}
 

