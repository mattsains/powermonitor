import spidev
import time

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
        response=[]
        for packet in [commandbyte]+list(data)+receive_bytes*[0]:
            response+=self.spidev.xfer([packet])

        response=response[len(data)+1:]
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

    """Returns two numbers representing the raw measurements from the current and voltage sensor"""
    def read_raw(self):
        response=self._send_data(0b001, 4)
        return { "CURRENT": response[0]<<8|response[1],
                 "VOLTAGE": response[2]<<8|response[3]
                 }

    """Returns the watts being used right now"""
    def read_watts(self):
        response=self._send_data(0b010, 2)
        return response[0]<<8|response[1]

    """Returns the measured power factor of the device (between -1 and 1)"""
    def read_power_factor(self):
        return self._send_data(0b011, 1) - 128

    """Returns a map containing the calibration paramaters. See specification for details"""
    """If something goes wrong, will throw an exception"""
    def read_calibration(self):
        response=self._send_data(0b100, 7)

        sum=0
        for byte in response[:-1]:
            sum+=byte
            
        if (sum!=response[-1]):
            raise Exception("IO Error", "The calibration parameter checksum was incorrect")

        return {
            "FILTER_STRENGTH": response[0],
            "SIGNAL_OFFSET": response[1]<<8|response[2],
            "CURRENT_SCALE": response[3],
            "VOLTAGE_SCALE": response[4],
            "VOLTAGE_PHASE_DELAY": response[5]
            }

    """Writes calibration parameters to the microcontroller"""
    def write_calibration(self, filter_strength, signal_offset, current_scale, voltage_scale, voltage_phase_delay):
        sum=(filter_strength+signal_offset+current_scale+voltage_scale+voltage_phase_delay)%256
        response=self._send_data(0b101, 1, filter_strength, signal_offset, current_scale, voltage_scale, voltage_phase_delay, sum)
        if (response!=0b10101010):
            raise Exception("IO Error", "Did not receive calibration write confirmation from the microcontroller - did it actually write?")
