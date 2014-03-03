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
int values[256]; //a buffer used for averaging the readings
byte pos=0; //where we are in the readings
int last; //what was the reading before this one?
byte writing=0; //are we currently reading/writing to these variables? (prevents clashes)

//Other code I wrote
#include "io.c"
#include "analog.c"



// When the microcontroller boots, this code runs
int main()
{
   setup_io(); //set up all the digital input/output pins
   setup_adc();
   
   //blink the LED to show aliveness

   statusLED1(1);
   for(;;)
   {
      _delay_ms(500);
      statusLED1(0);
      _delay_ms(500);
      statusLED1(1);
   }
}
