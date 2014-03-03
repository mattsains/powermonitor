//This code handles the measuring of the two/three analog inputs we have

//stores the analog input currently being measured.
byte current_channel; 

//Handles initialization of analog to digital hardware, ADC interrupts, 
// and other stuff needed to start measuring things
void setup_adc()
{
   
   current_channel=0;
   
   //Set the reference for analog conversions to the supply voltage (3.3V)
   //Open the AREF pin to use the stabilizing capacitor on that pin.
   //Right align the ADC output
   //Select the first analog input (ADC0)
   ADMUX=0b01000000;
   
   //Disable the digital circuitry on all analog input pins
   DIDR0=0b00111111;
   
   //Disable weird analog comparator stuff
   //Set the trigger mode to "free running" mode
   //This means that the completion of an ADC measurement will immediately trigger another
   ADCSRB=0;
   
   //Enable the analog to digital converter
   //Trigger the first conversion (the rest will be trigged by the end of the previous conversion)
   //Enable the auto trigger system (used for free running mode)
   //Enable the ADC interrupt (see ISR(ADC_vect))
   //Set up a /64 clock divider on the CPU clock speed of 8MHz for an ADC clock speed of 125kHz (max is 200kHz)
   ADCSRA=0b11101110;

   //enable interrupts
   sei();
   
   //at this point all the ADC hardware is configured and we will start seeing interrupts

   //time to set the scene for the next conversion, but first a wait is required to give the ADC unit time to sample the current signal
   _delay_loop_2(216); //delay for 864 clock cycles (13.5 ADC cycles)
   ADMUX=(ADMUX&~(0b111))|0b1; //fancy way to select the second ADC channel
}


//This is an Interrupt Service Routine (ISR)
// When an interrupt is triggered, the code is paused, and then this code is run.
//This code needs to be pretty fast - This entire method must be under 800 clock cycles because that's the delay between ADC results.
// This interrupt handles the interrupt that gets triggered when the microcontroller has
// finished measuring an analog input
ISR(ADC_vect)
{
   byte this_channel=current_channel;
   
   //Change to the next channel
   current_channel=current_channel==0?1:0;
   ADMUX=(ADMUX&~(0b111))|current_channel;
   
   //Get the conversion result
   //You must read ADCL first and then ADCH, 
   //because reading ADCL locks these registers until ADCH is read.
   //This prevents the result being updated between reading the registers.
   byte l=ADCL;
   byte h=ADCH;
   int result=(h<<8)|l;
   
   //TODO: handle the ADC result
   //The reading is stored in result
   //The corresponding channel is stored in this_channel
   
   while (writing==1){}
   writing=1;
   if (this_channel==0)
      last=result;
   else
   {
      values[pos]=last*result;
      pos=(pos+1)%256;
   }
   writing=0;
}
