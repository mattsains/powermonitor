//This file holds all the functions that deal with digital input and output pins

//Define where things are connected to the microcontroller
//These will change when the project is soldered together.
//The first status LED:
#define status1PORT PORTB
#define status1DDR DDRB
#define status1PIN 0
//The second status LED:
#define status2PORT PORTD
#define status2DDR DDRD
#define status2PIN 7
//the multiplexor
#define multiPORT PORTB
#define multiDDR DDRB
#define multiPIN 1

//This function sets up all the pin hardware
void setup_io()
{
   //initialization
   //pin modes
   status1DDR|=(1<<status1PIN);
   status2DDR|=(1<<status2PIN);
   multiDDR|=(1<<multiPIN);
   
   //zero everything
   status1PORT&=~(1<<status1PIN);
   status2PORT&=~(1<<status2PIN);
   multiPORT&=~(1<<multiPIN);
   
   //set up SPI
   //Enable the SPI
   //Enable the SPI interrupt
   //MSB first
   //Clock polarity: leading edge rising
   //Clock phase: Sample on leading edge
   //Clock polarity and phase might need to change, not sure what raspberry pi does
   SPCR=0b11000000;
}

//Lets you switch on/off the first status LED
//1 means on, 0 means off
void statusLED1(byte state)
{
   if (state==1)
      status1PORT|=(1<<status1PIN);
   else
      status1PORT&=~(1<<status1PIN);
}

//Lets you switch on/of the second LED
//1 means on, 0 means off
void statusLED2(byte state)
{
  if (state==1)
    status2PORT|=(1<<status2PIN);
  else
    status2PORT&=~(1<<status2PIN);
}

//Switches inputs on the multiplexor
void multiplex(byte channel)
{
   if (channel==1)
      multiPORT|=(1<<multiPIN);
   else
      multiPORT&=~(1<<multiPIN);
}


//SPI interrupt handler
ISR(SPI_STC_vect)
{
   //TODO: write the handler for receiving SPI data.
   //This data can be read from or written to the SPDR register
   while(writing==1){}
   writing=1;
   
   int average=0;
   byte i;
   for(i=0; i<pos;i++)
      average+=(values[i]/pos);
   SPDR=average>>8;
   writing=0;
}
