import serial

ser = serial.Serial('COM4', 9600)

while True:
    value = ser.readline()
    valueInString = value.decode('UTF-8')
    print(valueInString)