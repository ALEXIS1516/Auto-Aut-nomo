// PID DIRECCION DEL AUTOMOVIL AUTONOMO

//Librerías servo y sensor láser
#include <ESP32Servo.h>
#include "BluetoothSerial.h"
#include <Arduino.h>

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

#define IN1 12
#define IN2 27
#define ENA 14


BluetoothSerial SerialBT;

// Ganancias PID;
double Kp = 0.5, Ki = 5, Kd = 5;

// Variable posición
int pos = 0;

// Variables PID
unsigned long currentTime, previousTime;
double elapsedTime;
double error, lastError, cumError, rateError;
double outPut;

// Se define el servo y el sensor
Servo myservo;

void setup() {
  Serial.begin(115200);
  SerialBT.begin("NOVA Alexis");  // Iniciar el Bluetooth con el nombre "ESP32_BT"
  
  // Pin donde está conectado el servo
  myservo.attach(27);
  
  pinMode(IN1,OUTPUT);
  pinMode(IN2,OUTPUT);
  pinMode(ENA,OUTPUT);  
}

void loop() {

  if (Serial.available()) {    
    int c_x = SerialBT.parseInt();
    int h_x = SerialBT.parseInt();
    int led = SerialBT.parseInt();
    int puerta = SerialBT.parseInt();
    
    digitalWrite(IN1, HIGH);  // Sentido de giro hacia adelante
    digitalWrite(IN2, LOW);
    analogWrite(ENA, 80);  // Ajusta la velocidad del motor
    
    // Se asigna la posición del servomotor en grados 
    pos = PID(c_x,h_x) + 90;
    
    // Se limita el valor de la posición del servo para
    // que no exceda los límites
    limite();
    
    //Se manda la posición al servomotor
    myservo.write(pos);

    delay(20);
    // Se imprimen los valores para graficar en el serial plotter
   }
    
    digitalWrite(IN1, LOW);  // Sentido de giro hacia adelante
    digitalWrite(IN2, LOW);
    analogWrite(ENA, 0);  // Ajusta la velocidad del motor
    delay(20);
}

void limite(void)
{ 
  // Si la posición se pasa de 130 que se mantenga en 130
  if (pos > 130)
  {
    pos = 130;
  }
  // Si la posición es menos de 60 que se mandenga en 60
  if (pos < 50)
  {
    pos = 50;
  }
}

double PID(float setPoint, float input)
{ 
  // Se guarda el tempo actual 
  currentTime = millis();
  // Se calcula el tiempo transcurrido
  elapsedTime = currentTime - previousTime;

  // Se obtiene el error de posición
  error = setPoint - input;
  // Se calcula la integral del error
  cumError += error * elapsedTime;
  // Se calcula la derivada del error
  rateError = (error - lastError) / elapsedTime;
  // Se calcula la salida del controlador
  outPut = Kp * error + Ki * cumError + Kd * rateError;

  // El error actual se convierte en el error pasado
  lastError = error;
  // El tiempo actual se convierte en el tiempo pasado
  previousTime = currentTime;

  // Se regresa la salida del controlador
  return outPut;
}
