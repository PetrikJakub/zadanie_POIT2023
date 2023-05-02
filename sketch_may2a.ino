const int trigPin = 12; 
const int echoPin = 11; 
const int fotoresistorPin = A0; 
int hodnotaSvetla; 

void setup() {
  Serial.begin(9600); 
  pinMode(trigPin, OUTPUT); 
  pinMode(echoPin, INPUT); 
}

void loop() {
  hodnotaSvetla = analogRead(fotoresistorPin);
  digitalWrite(trigPin, LOW); 
  delayMicroseconds(2); 
  digitalWrite(trigPin, HIGH); 
  delayMicroseconds(10); 
  digitalWrite(trigPin, LOW); 
  long duration = pulseIn(echoPin, HIGH); 
  int vzdalenost = duration * 0.034 / 2; 
  // Serial.print("Hodnota svetla: "); 
  Serial.print(hodnotaSvetla); 
  Serial.print(","); 
  // Serial.print("Vzdalenost: ");
  Serial.println(vzdalenost); 
  // Serial.println(" cm"); 
  delay(500); 
}