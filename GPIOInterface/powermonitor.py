import spidev

class PowerMonitor:
    def __init__(self):
        self.spidev=spidev.SpiDev()
        self.spidev.open(0,1)
    
    """Internal wrapper function used to format the command byte"""
    def _send_data(self, command, receive_bytes, *data):
        commandbyte=0b10100010|(command<<2)
        checksum=(((command>>2)&1)^
                  ((command>>1)&1)^
                  ((command>>0)&1))
        commandbyte+=checksum
        self.spidev.writebytes([command]+list(data))

        response=self.spidev.readbytes(receive_bytes)
        if (receive_bytes==1):
            return response[0]
        else:
            return response
    
    """Performs a handshake with the microcontroller. It is recommended to do this make sure the microcontroller is actually there"""
    """Returns a map with keys 'HIGH_CURRENT', 'OVER_CURRENT' and 'NO_VOLTAGE', or false if no valid response was received"""
    def handshake(self):
        response=self._send_data(0b000, 1)
        
        if (response&(1<<7) and not response&1):
            return {
                "HIGH_CURRENT": bool(response&(1<<1)),
                "OVER_CURRENT": bool(response&(1<<2)),
                  "NO_VOLTAGE": bool(response&(1<<3))
            }
        else:
            return False
