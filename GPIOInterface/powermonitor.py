import spidev
import ctypes


class PowerMonitor:
    def __init__(self):
        self.spidev = spidev.SpiDev()
        self.spidev.open(0, 1)

    def _send_data(self, command, receive_bytes, *data):
        """Internal wrapper function used to format the command byte"""
        commandbyte = 0b10100010 | (command << 2)
        checksum = (((command >> 2) & 1) ^
                    ((command >> 1) & 1) ^
                    ((command >> 0) & 1))
        commandbyte += checksum
        response = []
        for packet in [commandbyte] + list(data) + receive_bytes * [0]:
            response += self.spidev.xfer([packet])

        response = response[len(data) + 1:]
        if receive_bytes == 1:
            return response[0]
        else:
            return response

    def handshake(self):
        """Performs a handshake with the microcontroller. It is recommended to do this make sure the microcontroller is
        actually there. Returns a map with keys 'HIGH_CURRENT', 'OVER_CURRENT' and 'NO_VOLTAGE', or false if no valid
        response was received"""
        response = self._send_data(0b000, 1)

        if response & 1 << 7 and not response & 1:
            return {
                "HIGH_CURRENT": bool(response & (1 << 1)),
                "OVER_CURRENT": bool(response & (1 << 2)),
                "NO_VOLTAGE": bool(response & (1 << 3))
            }
        else:
            return False

    def read_raw(self):
        """Returns two numbers representing the raw measurements from the current and voltage sensor"""
        response = self._send_data(0b001, 4)
        return {
            "CURRENT": response[0] << 8 | response[1],
            "VOLTAGE": response[2] << 8 | response[3]
        }

    def read_watts(self):
        """Returns the watts being used right now"""
        response = self._send_data(0b010, 2)
        return ctypes.c_int16(response[0] << 8 | response[1]).value

    def read_power_factor(self):
        """Returns the measured power factor of the device (between -1 and 1)"""
        return self._send_data(0b011, 1) - 128

    def read_calibration(self):
        """Returns a map containing the calibration paramaters. See specification for details
        If something goes wrong, will throw an exception"""
        response = self._send_data(0b100, 9)

        sum = 0
        for byte in response[:-1]:
            sum += byte

        if sum & 0xFF != response[-1]:
            raise Exception("IO Error", "The calibration parameter checksum was incorrect")

        return {
            "FILTER_STRENGTH": response[0],
            "SIGNAL_OFFSET": (response[1] << 8) | response[2],
            "CURRENT_SCALE": (response[3] << 8) | response[4],
            "VOLTAGE_SCALE": (response[5] << 8) | response[6],
            "VOLTAGE_PHASE_DELAY": response[7]
        }

    def write_calibration(self, filter_strength, signal_offset, current_scale, voltage_scale, voltage_phase_delay):
        """Writes calibration parameters to the microcontroller"""
        signal_offset_high=signal_offset>>8
        signal_offset_low=signal_offset&0xFF
        current_scale_high=current_scale>>8
        current_scale_low=current_scale&0xFF
        voltage_scale_high=voltage_scale>>8
        voltage_scale_low=voltage_scale&0xFF
        sum = (filter_strength + signal_offset_high + signal_offset_low + current_scale_high + current_scale_low + voltage_scale_high + voltage_scale_low + voltage_phase_delay) % 256
        response = self._send_data(0b101, 1, filter_strength, signal_offset_high, signal_offset_low, current_scale_high, current_scale_low, voltage_scale_high, voltage_scale_low, voltage_phase_delay, sum)
        return response
        if response != 0b10101010:
            raise Exception("IO Error",
                            "Did not receive calibration write confirmation from the microcontroller - did it actually "
                            "write?")
