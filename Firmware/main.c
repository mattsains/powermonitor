#include <avr/io.h>   //defines the registers we can access
#include <stdint.h>   //defines some data types like int and long
#include <avr/interrupt.h> //lets us use interrupts
#include <util/delay.h> //lets us make delays

//#define statements are like constant variables - well more like search and replace on code
//the left hand side becomes the right hand side everywhere it is typed in code
//It works like a constant because if you have #define x 6, 
// a statement like add(x,x) becomes add(6,6)
#define F_CPU 8000000L //The delay library needs to know the clock speed - it's 8MHz

//Other code I wrote
#include "io.c"
#include "analog.c"

// When the microcontroller boots, this code runs
int main()
{
   setup_io(); //set up all the digital input/output pins
   
   //turn on the status LED to show "ready" or something
   statusLED(true);
}