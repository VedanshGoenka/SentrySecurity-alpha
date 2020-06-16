/* ReadAnalogVoltage 0 to 50 Volts - blog.circuits4you.com

     Reads an analog input on pin 0, converts it to voltage, and prints the  

     result to the serial monitor.

     Graphical representation is available using serial plotter   (Tools >   

     Serial Plotter menu)*/



// the setup routine runs once when you press reset:

void setup() {

  // initialize serial communication at 9600 bits per second:

  Serial.begin(9600);

}

int stableRead(int pin) {
  int value = 0;
  int samples = 10;
  for (int i=0; i<samples; i++) {
    value += analogRead(pin);
    delay(1);
  }
  return value / samples;
}

void loop() {

  int sensors = 8;
  int sensorValues [] = {
    stableRead(A2), stableRead(A3), stableRead(A4), stableRead(A6),
    stableRead(A7), stableRead(A8), stableRead(A9), stableRead(A10)
  };

  float voltages [sensors];
  for (int v=0; v<sensors; v++) {
    voltages[v] = sensorValues[v] * (5.0 / 1024.0) * 1;
  }
  // print out the value you read:
  for (int i=0;i<sensors;i++) {
     Serial.print(i+1);
     Serial.print(":");
     Serial.print(voltages[i]);
     Serial.print(", ");
  }
  Serial.println();
  delay(1000);

}
