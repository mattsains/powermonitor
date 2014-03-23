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

void read_eeprom_calibration(); //this is defined in analog.c

//Reads a value from EEPROM
byte read_eeprom(byte address)
{
   cli();
   while (EECR & 2); //wait until any writes are finished
   EEARL=address; //set the EEPROM address register
   EECR|=1; //set the read bit in the EEPROM control register
   byte result=EEDR;
   sei();
   return result;
}

//Write a value to EEPROM
void write_eeprom(byte address, byte value)
{
   cli();
   while (EECR & 2); //wait until any other writes are finished
   EEARL=address;
   EEDR=value;
   EECR|=1<<2; //set the master write enable bit
   EECR|=1<<1; //set the write bit
   sei();
}

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
   //first set up some port direction stuff:
   DDRB|=1<<4; //MISO as output
   //Enable the SPI interrupt
   //MSB first
   //Clock polarity: leading edge rising
   //Clock phase: Sample on leading edge
   //Clock polarity and phase might need to change, not sure what raspberry pi does
   SPCR=0b11000000;

   //enable interrupts
   sei();
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

//Some SPI state variables
byte transaction;
byte data_buffer_pos;
byte data_buffer[8];

//Handles the SPI data received interrupt
ISR(SPI_STC_vect)
{
   //TODO: write the handler for receiving SPI data.
   //This data can be read from or written to the SPDR register

   byte data_in=SPDR;
   statusLED2(transaction!=0);

   if (transaction==0)
   {
      //A new transaction is beginning
      statusLED2(data_in!=0);
      if (data_in==0b10100010)
      {
	 //Handshake
	 byte no_voltage=(100.0*(max_voltage-min_voltage))/(256+voltage_scale) < 200;
	 SPDR=0b10000000|(no_voltage<<3) //no voltage sense flag
	                |((max_sense==1023)<<2) //overcurrent flag
	                |((current_mode==0)<<1); //high current flag
      }
      else if (data_in==0b10100111)
      {
	 //Read raw
	 SPDR=last_current>>8;
	 //Remember next few bytes
	 data_buffer[0]=last_current&0xFF;
	 data_buffer[1]=last_voltage>>8;
	 data_buffer[2]=last_voltage&0xFF;
	 transaction=1;
	 data_buffer_pos=0;
      }
      else if (data_in==0b10101011)
      {
	 //Read watts
	 SPDR=filter_watts>>8;
	 //Remember next byte
	 data_buffer[0]=filter_watts&0xFF;
	 transaction=2;
      }
      else if (data_in==0b10101110)
      {
	 //Read power factor
	 SPDR=0;//not implemented yet
      }
      else if (data_in==0b10110011)
      {
	 //Read calibration numbers
	 byte sum=read_eeprom(1);
	 SPDR=sum;
	 for (byte i=0; i<5; i++)
	 {
	    data_buffer[i]=read_eeprom(i+2);
	    sum+=data_buffer[i];
	 }
	 data_buffer[5]=sum;
	 transaction=3;
	 data_buffer_pos=0;
      }
      else if (data_in==0b10110110)
      {
	 //Write new calibration
	 transaction=4;
	 data_buffer_pos=0;
      }
   }
   else if (transaction==1)
   {
      //continuing Read raw
      SPDR=data_buffer[data_buffer_pos++];
      if (data_buffer_pos>2)
	 transaction=0;
   }
   else if (transaction==2)
   {
      //continuing Read watts
      SPDR=data_buffer[0];
      transaction=0;
   }
   else if (transaction==3)
   {
      //continuing Read calibration numbers
      SPDR=data_buffer[data_buffer_pos++];
      if (data_buffer_pos>5)
	 transaction=0;
   }
   else if (transaction==4)
   {
      //continuing Write calibration numbers
      data_buffer[data_buffer_pos++]=SPDR;
      if (data_buffer_pos==7)
      {
	 transaction=0;
	 byte sum=0;
	 for(byte i=0; i<6; i++)
	    sum+=data_buffer[i];
	 if (sum!=data_buffer[6])
	    SPDR=0; //checksum error
	 else
	 {
	    //write these new values
	    write_eeprom(0,0);
	    for(byte i=0; i<6; i++)
	       write_eeprom(i+1,data_buffer[i]);
	    write_eeprom(0,0xCA); //magic value

	    read_eeprom_calibration();
	    SPDR=0b10101010; //send back calibration done
	 }
      }
   }
}
