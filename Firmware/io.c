//This file holds all the functions that deal with digital input and output pins

//Define where things are connected to the microcontroller
//These will change when the project is soldered together.
//The status LED:
#define statusPORT PORTB
#define statusDDR DDRB
#define statusPIN 0

//This function sets up all the pin hardware
void setup_io()
{
   //initialization
   //pin modes
   statusDDR|=(1<<statusPIN);
}

//Lets you switch on/off the status LED
void statusLED(bool state)
{
   if (state==true)
      statusPORT|=(1<<statusPIN);
   else
      statusPORT&=~(1<<statusPIN);
}