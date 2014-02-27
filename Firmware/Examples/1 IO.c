#include <avr/io.h> //defines the registers we can access

//When the microcontroller boots, it runs this code
//This code blinks an LED.
int main()
{
   //The wires coming out of the microcontroller are in groups of eight pins called "ports."
   //each port has an eight-bit register that we can put a number into.
   //Our microcontroller has port B, C, and D.
   //each bit of this number corresponds to a pin.
   //A 1 will make the microcontroller push electricity out of the corresponding pin. (Positive voltage)
   //A 0 will make the microcontroller try to neutralize any electricity on the corresponding pin. (zero volts aka ground)
   
   //Let's say we have an LED connected to port B on the second (oneth) bit.
   //First we have to set that pin so that it is used as output and not as input.
   //When the microcontroller starts, all pins are inputs. This is good because an input pin does not interfere with what's going on electrically. You don't want a pin to force electricity on a component that can't handle it.
   
   //We first set the "Data Direction" register for pin 2 of port b to output.
   //Here, a binary 1 means output and 0 means input
   DDRB=0b00000010; //this is how you write binary in C/C#.
   
   //The pin is now in output mode and will be trying to neutralize the electrical charge on the wire.
   //From now on I will call this the LOW state, and pushing electricity out is called the HIGH state.
   //Let's assume the LED is wired up so that this setup causes the LED to be OFF.
   
   //Switch on the LED by setting the second bit on the port's register to 1:
   PORTB=0b00000010;
   
   //Now the pin is actively pushing electricity out. It is in a HIGH state.
   //It is pushing electricity through the LED and so the LED is ON.
   
   //Let's make it blink
   
   while (true)
   {
      PORTB=0b00000000; //off, LOW, neutralizing
      
      some_delay_function(1000);
      //There is a delay function, but it depends on the clock speed because the microcontroller has no real time clock! (you have to make it yourself)
      
      PORTB=0b00000010; //on, HIGH, pushing
      
      some_delay_function(1000);
   }
   //It's pretty bad practice to set the entire PORTB register, because it sets all the other pins to zero - pins you might be using at the same time.
   //You should rather use fancy binary maths, like this:
   
   //To turn on:
   PORTB=PORTB | 0b00000010; //PORTB or 0b10
   
   //To turn off:
   PORTB=PORTB & 0b1111101; //PORTB and not(0b10)
   //alternatively:
   PORTB=PORTB & ~(0b00000010); //PORTB and not(0b10)
   //the shortest way:
   PORTB&=~(2);
   
   //Using bitshifts (google that) you can make this much more readable:
   
   //switch on pin 2:
   PORTB|=(1<<2);
   
   //switch on pin 2 and 4:
   PORTB|=(1<<2)|(1<<4);
   
   //switch off 4:
   PORTB&=~(1<<4);
   
}