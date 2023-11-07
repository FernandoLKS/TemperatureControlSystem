import serial

def dac_initialize(port='/dev/ttyUSB0'):
    MAGIC_CODE = 'AARC1'
    p = serial.Serial(port, baudrate=115200, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE, timeout=5)

    version = p.readline()
    print(f"Version: {version}")

    if len(version) < len(MAGIC_CODE) or version[0:len(MAGIC_CODE)].decode('utf8') != MAGIC_CODE:
        raise Exception('Failed to get {} magic code. Got {} instead.'.format(MAGIC_CODE,version))

    return p, version

def dac_send_data(port, pin, value):
    CMD_WRITE_DAC = 0
    # limit input for 6 pins
    if value < 0:
        value = 0
    elif value > 5:
        value = 5

    # Scale output data to range 0 - 255 (1 byte) for arduino
    data = int(round(value*(255.0/5.0)))

    # Sends CMD_WRITE_DAC command, desired pin and data value
    cmd = (CMD_WRITE_DAC).to_bytes(1, byteorder='little') + int(pin).to_bytes(1, byteorder='little') + int(data).to_bytes(1, byteorder='little')
    port.write(cmd)
    # no need to flush, we don't need to wait for data to be written

def dac_receive_data(port, pin, block=False):
    CMD_READ_ADC = 1
    # Sends CMD_READ_DAC command and desired pin
    cmd = (CMD_READ_ADC).to_bytes(1, byteorder='little') + int(pin).to_bytes(1, byteorder='little')
    port.write(cmd)
    port.flush()

    bytesL = port.read(2 if port.in_waiting or block else 0)
    #bytesL = port.read()
    #print('input {} {}'.format(len(bytesL), bytesL.hex()))
    # get reply - may be done blocking or nonblocking
    value = int.from_bytes(bytesL, byteorder='little')
    #print(value)
    # Scale Arduino 10 bit input to range 0 - 5
    # Analog input readings are returned as 10-bit integer values.
    # The maximum numerical value for a (unsigned) 10-bit number is 1023.
    data = value*(5.0/1023.0)/0.01

    return data

def dac_receive_all(port, block=False):
    CMD_READ_ALL_ADC = 2
    # Sends CMD_READ_ALL_DAC command and desired pin
    cmd = (CMD_READ_ALL_ADC).to_bytes(1, byteorder='little')
    port.write(cmd)
    port.flush()

    # non-blockig get reply
    pinCount = int.from_bytes(port.read(1 if port.in_waiting or block else 0), byteorder='little')
    data = [int.from_bytes(port.read(2 if port.in_waiting or block else 0), byteorder='little')*(5.0/1023.0) for pin in range(pinCount)]

    return data