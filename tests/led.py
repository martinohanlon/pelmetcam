import RPi.GPIO as GPIO
import time
import threading
import os
import sys

# constants
SLOWFLASHTIMES = [2,2]
FASTFLASHTIMES = [0.5,0.5]

# class for managing LED
class LEDControl():
    class LEDStates():
        #states of LED
        OFF = 0
        ON = 1
        FLASH = 2
        
    def __init__(self, gpioPin):
        #init gpio
        self.gpioPin = gpioPin
	# setup gpio pin as output
        GPIO.setup(self.gpioPin, GPIO.OUT)
        #set led to off
        self.off()

    def set(self, ledValue):
        #Sets the value of the LED [True / False]
        self.ledValue = ledValue
        GPIO.output(self.gpioPin, self.ledValue)

    def get(self):
        #Gets the value of the led
        return self.ledValue

    def on(self):
        #Turns the LED on
        self.state = self.LEDStates.ON
        self.set(True)

    def off(self):
        #Turns the LED off
        self.state = self.LEDStates.OFF
        self.set(False)

    def flash(self, timeOn, timeOff):
        #if the led is already flashing, set it to off and wait for it to stop
        if self.state == self.LEDStates.FLASH:
            self.off()
            self.flashthread.join()
        # flash the LED on a thread
        self.state = self.LEDStates.FLASH
        self.flashthread = threading.Thread(target=self.__flashLED, args=(timeOn, timeOff))
        self.flashthread.start()

    def __flashLED(self, timeOn, timeOff):
        #loops untils the LED is changed from FLASH (i.e. on or off)
        while self.state == self.LEDStates.FLASH:
            if self.get() == True:
                self.set(False)
                time.sleep(timeOff)
            else:
                self.set(True)
                time.sleep(timeOn)
    	
    def toggle(self):
        #Toggles the LED, if its on, turns it off and vice versa
        if self.get == True: self.off()
        else: self.on()

if __name__ == "__main__":

    try:

        #set gpio mode
        GPIO.setmode(GPIO.BCM)

        #create LED
        led = LEDControl(17)
                           
        while(True):
            led.on()
            time.sleep(1)
            led.off()
            time.sleep(1)
        
    except KeyboardInterrupt:
        print "User Cancelled (Ctrl C)"
        
    except:
        print "Unexpected error - ", sys.exc_info()[0], sys.exc_info()[1]
        raise
    
    finally:
        #turn off led
        led.off()
        #cleanup gpio
        GPIO.cleanup()
        print "Stopped"
