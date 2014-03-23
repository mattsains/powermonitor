//#define statements are like constant variables - well more like search and replace on code
//the left hand side becomes the right hand side everywhere it is typed in code
//It works like a constant because if you have #define x 6, 
// a statement like add(x,x) becomes add(6,6)
#define F_CPU 8000000L //The delay library needs to know the clock speed - it's 8MHz

//Libraries
#include <avr/io.h>   //defines the registers we can access
#include <stdint.h>   //defines some data types like int and long
#include <avr/interrupt.h> //lets us use interrupts
#include <util/delay.h> //lets us make delays

//Some conveniences
#define byte unsigned char

//global variables
//Analog calculation variables
int last_current;
byte last_current_mode;
int last_voltage;
long int filter_watts;
//Intellent sensing variables
byte current_mode; //0: high current; 1: low current
int max_sense; //highest reading returned. This gets reset when modes are switched

byte voltage_range_reset;
int max_voltage;
int min_voltage=1024;
byte voltage_scale;

//Other code I wrote
#include "io.c"
#include "analog.c"



// When the microcontroller boots, this code runs
int main()
{
   setup_io(); //set up all the digital input/output pins
   setup_adc(); //set up the analog to digital conversion
   statusLED1(1);
   //spin wait - otherwise the processor dies
   for(;;)
   {
      statusLED1(current_mode);
   }
}
