#include <Arduino.h>
#include <LiquidCrystal.h>

LiquidCrystal lcd(12, 13, 7, 6, 5, 4);

/**/
const uint8_t CMD_WRITE_DAC = 0;
const uint8_t CMD_READ_ADC = 1;
const uint8_t CMD_READ_ALL_ADC = 2;
const uint8_t CMD_WRITE_REFERENCE = 3;

const uint8_t DAC_COUNT = 6;
const uint8_t ADC_COUNT = 6;

// ARDUINO NANO
uint8_t dacPins[] = {8}; // output digital PWM pins D3, D5, D6, D9, D10, D11
uint8_t adcPins[] = {PIN_A0}; // input analog pins
uint16_t inValuesBuffer[ADC_COUNT] = {0};

uint8_t Lpin = LED_BUILTIN;

uint8_t inPin = 0;
uint8_t inValue = 0;
uint16_t adcValue = 0;
volatile uint16_t inputValue = 0;

uint16_t i = 0;

float TempReferencia = 35;
int DutyCicle = 100; 

void setup()
{
  // Set input and output pins
  pinMode(Lpin, OUTPUT);

  for(i = 0; i < DAC_COUNT; i++)
    pinMode(dacPins[i], OUTPUT);

  for(i = 0; i < ADC_COUNT; i++)
    pinMode(adcPins[i], INPUT);

  // Blink 5 times to identify this program
  for(i = 0; i < 5; i++)
  {
    digitalWrite(Lpin, HIGH);
    delay(100);
    digitalWrite(Lpin, LOW);
    delay(100);
  }
  lcd.begin(16, 2);

  // Open serial communications
  Serial.begin(115200, SERIAL_8N1);
  // Wait for serial port to connect. Needed for native USB port only (TODO: is this really necessary?)
  while (!Serial) ;
  Serial.println("AARC1");
}

inline void waitSerialAvailable()
{
  // busy wait for data
  while(!Serial.available()) ;
}

void loop()
{ 
  float valorSensor = analogRead(adcPins[0]);
 
  float Tensao = (valorSensor * 5) / 1023; 
  float TempAmbiente = Tensao / 0.010;

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("R ");
  lcd.print(TempReferencia, 1); 
  lcd.print("C  ");
  lcd.print("A ");
  lcd.print(TempAmbiente, 1);
  lcd.print("C  ");
  lcd.setCursor(0, 1);
  lcd.print("DutyC: ");
  lcd.print(DutyCicle);
  lcd.print("%"); 

  delay(100);

  // Wait for command
  if(Serial.available())
  {
    // Read command
    inValue = Serial.read();

    switch(inValue)
    {
      case CMD_WRITE_DAC:
      {
        // Receive a pin value (0 to DAC_COUNT-1) and an output value (0-255)
        waitSerialAvailable();
        inPin = Serial.read();
        waitSerialAvailable();
        inValue = Serial.read();
        DutyCicle = inValue*100/255;

        // Output the desired pin with the PWM cycle
        if(inPin >= 0 && inPin <= DAC_COUNT-1)
          analogWrite(dacPins[inPin], inValue);
      }break;
      case CMD_READ_ADC:
      {
        // Receive a pin value
		    waitSerialAvailable();
        inPin = Serial.read();

        if(inPin >= 0 && inPin <= ADC_COUNT-1)
        {
          // Read the desired analog pin
          adcValue = analogRead(adcPins[inPin]);
          
          // Send the analog value (for ATMEL328P this is a 16 bit value in little endian)
          Serial.write((uint8_t*)&adcValue, sizeof(adcValue));
        }
      }break;
      case CMD_READ_ALL_ADC:
      {
        // Read all analog pins
        for(i = 0; i < ADC_COUNT; i++)
          inValuesBuffer[i] = analogRead(adcPins[i]);

        // Send the analog values
        Serial.write((uint8_t*)&ADC_COUNT, sizeof(ADC_COUNT));
        Serial.write((uint8_t*)&inValuesBuffer, sizeof(inValuesBuffer));
      }break;
      case CMD_WRITE_REFERENCE:
      {
        waitSerialAvailable();
        TempReferencia = Serial.read();
      }
    }
  }
}
