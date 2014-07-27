flash: compile
	avrdude -c linuxspi -P /dev/spidev0.0 -p m48pa -e -U flash:w:firmware.bin
compile:
	avr-gcc -O3 -ffunction-sections -fdata-sections -fpack-struct -Wall -std=gnu99 -s -mmcu=atmega48p main.c -o main.elf
	avr-objcopy -j .text -j .data -O binary main.elf firmware.bin
clean:
	rm -f main.elf firmware.bin
