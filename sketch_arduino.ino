const int trigPin = 12;
const int echoPin = 11;
const int fotoresistorPin = A0;
int hodnotaSvetla;
float hodnotaSvetlado100;

void setup() {
  Serial.begin(9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  delay(500);
}

void loop() {
  hodnotaSvetla = analogRead(fotoresistorPin);
  hodnotaSvetlado100 = (hodnotaSvetla / 1024.0) * 100.0; 
 
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  long duration = pulseIn(echoPin, HIGH);
  
  int vzdalenost = duration * 0.034 / 2;
  if (vzdalenost > 300){
    vzdalenost = 300;
  }
  
  Serial.print(hodnotaSvetlado100, 2); 
  Serial.print(","); 
  // Serial.print("Vzdalenost: ");
  Serial.println(vzdalenost); 
  // Serial.println(" cm"); 
  delay(2000); 
}
