//This file holds all the functions that deal with digital input and output pins

//Define where things are connected to the microcontroller
//These will change when the project is soldered together.
//The status LED:
#define statusPORT PORTB
#define statusDDR DDRB
#define statusPIN 0
//the multiplexor
#define multiPORT PORTB
#define multiDDR DDRB
#define multiPIN 1

//This function sets up all the pin hardware
void setup_io()
{
   //initialization
   //pin modes
   statusDDR|=(1<<statusPIN);
   multiDDR|=(1<<multiPIN);
   
   //zero everything
   statusPORT&=~(1<<statusPIN);
   multiPORT&=~(1<<multiPIN);
}

//Lets you switch on/off the status LED
//1 means on, 0 means off
void statusLED(byte state)
{
   if (state==1)
      statusPORT|=(1<<statusPIN);
   else
      statusPORT&=~(1<<statusPIN);
}

//Switches inputs on the multiplexor
void multiplex(byte channel)
{
   if (channel==1)
      multiPORT|=(1<<multiPIN);
   else
      multiPORT&=~(1<<statusPIN);
}