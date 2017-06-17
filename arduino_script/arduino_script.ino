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
int val = 0;       // variable to store the value coming from the sensor
int tempVal = -1;
int serialRate = 9600;
int updateRate = 200;
String return_type = "number";
char byteRead;
void setup() {
  Serial.begin(serialRate);
  // First Value
  updatePotentiometerValue();
  returnValue();
}

void loop() {
  updatePotentiometerValue();
  checkRequestAndReturn();
  delay(updateRate);                  // stop the program for some time
}

void checkRequestAndReturn() {
  if (Serial.available()) {
    byteRead = Serial.read();
    if(byteRead == '1') {
      Serial.println(formatReturn());
    }
  }
}

void returnValue() {
  Serial.println(formatReturn());
}

void updatePotentiometerValue() {
  val = analogRead(potPin);    // read the value from the sensor
  if(val!=tempVal) {
    tempVal = val;
  }
}

String formatReturn() {
  String _return = (String)"return_type:" + return_type + (String)",val:" + String(val);
  return _return;
}
 

