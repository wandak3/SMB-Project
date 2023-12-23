#!/usr/bin/python
import smbus
from time import sleep
import RPi.GPIO as GPIO

# Define some constants for the motor driver
DIR = 20   # Direction GPIO Pin
STEP = 21  # Step GPIO Pin
CW = 1     # Clockwise Rotation
CCW = 0    # Counterclockwise Rotation
SPR = 200  # Steps per Revolution (360 / 1.8)

# Initialize the motor driver
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)

step_count = SPR * 5
delay = 0.0009
closed_or_openedFLAG = 0 # 0 means curtain is currently open, 1 means currently closed

# Define some constants from the datasheet
DEVICE     = 0x23 # Default device's I2C address
POWER_DOWN = 0x00 # No active state
POWER_ON   = 0x01 # Power on
RESET      = 0x07 # Reset data register value
 
# Start measurement at 4lx resolution. Time typically 16ms.
CONTINUOUS_LOW_RES_MODE = 0x13

# Start measurement at 1lx resolution. Time typically 120ms
CONTINUOUS_HIGH_RES_MODE_1 = 0x10

# Start measurement at 0.5lx resolution. Time typically 120ms
CONTINUOUS_HIGH_RES_MODE_2 = 0x11

# Start measurement at 1lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement.
ONE_TIME_HIGH_RES_MODE_1 = 0x20

# Start measurement at 0.5lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement.
ONE_TIME_HIGH_RES_MODE_2 = 0x21

# Start measurement at 1lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement
ONE_TIME_LOW_RES_MODE = 0x23
 
#bus = smbus.SMBus(0) # Rev 1 Pi uses 0
bus = smbus.SMBus(1)  # Rev 2 Pi uses 1 (also apply to Rpi 3B 2015)

# Define the maximum brightness level that would
# cause the curtain to close all the way
maxBrightness = 65000 # not sure, might need to check and re-adjust
 
def convertToNumber(data):
  # Simple function to convert 2 bytes of data into a float decimal number
  return ((data[1] + (256 * data[0])) / 1.2)
 
def readLight(addr=DEVICE): # input is by default the device's I2C address
  # Just need to know that this function returns a float decimal number
  data = bus.read_i2c_block_data(addr,ONE_TIME_HIGH_RES_MODE_1)
  return convertToNumber(data)
 
def main(): # Everything in main()
  while True: # Python's version of a loop that runs forever
    print("Light Level : " + str(readLight()) + " lux")
    # Continuously updated variable on what percentage brightness is present
    curtainPercent = readLight()/maxBrightness

    if ((closed_or_openedFLAG == 0) and (curtainPercent > 0.5)):
      GPIO.output(DIR, CW)
      for x in range(step_count):
        GPIO.output(STEP, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        sleep(delay)
    elif ((closed_or_openedFLAG == 1) and (curtainPercent <= 0.5)):
      GPIO.output(DIR, CCW)
      for x in range(step_count):
        GPIO.output(STEP, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        sleep(delay)

    sleep(60) # Should change this time interval between measurements to be longer
  

if __name__=="__main__": # Don't understand, need help
   main()
