flash: compile
	avrdude -c linuxspi -P /dev/spidev0.0 -p m48pa -e -U flash:w:firmware.bin
compile:
	avr-gcc -s -mmcu=atmega48p -Os main.c -o main.elf
	avr-objcopy -j .text -j .data -O binary main.elf firmware.bin
clean:
	rm -f main.elf firmware.bin
