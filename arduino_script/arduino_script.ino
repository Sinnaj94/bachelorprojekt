/*
 * Arduino Sensor Request
 * by Jannis Jahr, 2017
 */

int potPin = 2;    // select the input pin for the potentiometer (Analog)
int switchPin = 2; // Select the input pin for the Button (Digital)
int valButton = 0; // variable to store the value of button
int valPoti = 0; // variable to store the value coming from the Potentiometer
int serialRate = 9600; // Baud Rate used by PySerial later
// Update Rate
int updateRate = 200; // Update rate in Miliseconds
char requestDigit; // 

// First start of Arduino
void setup() {
  Serial.begin(serialRate);
  // define as switch button
  pinMode(switchPin,INPUT_PULLUP);
  // First Value
  updatePotentiometerValue();
  updateButtonValue();
}

// Loop function that gets executed after setup
void loop() {
  // Update Values
  updatePotentiometerValue();
  updateButtonValue();
  checkRequestAndReturn();
  // Stop the program for some time
  delay(updateRate);
}

// Update the Potentiometer Value
void updatePotentiometerValue() {
  valPoti = analogRead(potPin);
}

// Update the Button Value
void updateButtonValue() {
  valButton = digitalRead(switchPin);
}

// Actual Request Pattern. Check if there was an Input and send the right Value via Serial Connection if there was one
void checkRequestAndReturn() {
  // Check if serial Connection is available and send answer, if there was a Serial.Read()
  if (Serial.available()) {
    requestDigit = Serial.read();
    if(requestDigit == '1') {
      Serial.println(formatReturn(valPoti));
    }else if(requestDigit == '2') {
      Serial.println(formatReturn(invertValue(valButton)));
    }
  }
}

// Convert int to a String to Write it to the serial Connection
String formatReturn(int returned_val) {
  return String(returned_val);
}

// Invert the Button, because it is 1 when off and 0 when on
int invertValue(int value) {
  return value==1?0:1;
}
 

