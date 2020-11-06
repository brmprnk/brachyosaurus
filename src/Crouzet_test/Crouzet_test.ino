/* Moves the stepper motor approx 1cm forward or 12 
 *  revolutions times 24 steps
 *  by Florens Helfferich & Bram Pronk 23/10/2020
 */

const int stepsPerRev = 12*24;
const int stepPin = 2;
const int dirPin = 3;

void setup() {
  // put your setup code here, to run once:
pinMode(13, OUTPUT);
pinMode(12, OUTPUT);
pinMode(3, OUTPUT);
pinMode(2, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
digitalWrite(dirPin, HIGH);
for(int x = 0; x <stepsPerRev; x++) { 
  digitalWrite(stepPin, HIGH);
  delay(50);
  digitalWrite(stepPin,LOW);
  delay(50);
}
delay(1000);
// going the other way
digitalWrite(dirPin, LOW);
for(int x = 0; x <stepsPerRev; x++) { 
  digitalWrite(stepPin, HIGH);
  delay(50);
  digitalWrite(stepPin,LOW);
  delay(50);
}
delay(1000);
}
