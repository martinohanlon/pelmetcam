import time
import threading
import RPi.GPIO as GPIO
import sys

BUTTONSHORTPRESSTICKS = 5
BUTTONLONGPRESSTICKS = 200
BUTTONTICKTIME = 0.01

# class for managing the Button
class ButtonControl(threading.Thread):
    class ButtonPressStates():
        NOTPRESSED = 0
        SHORTPRESS = 1
        LONGPRESS = 2
    def __init__(self, gpioPin, pressedState, shortPressTicks, longPressTicks, tickTime):
        #setup threading
        threading.Thread.__init__(self)
        #persist data
        self.gpioPin = gpioPin
        self.pressedState = pressedState
        self.shortPressTicks = shortPressTicks
        self.longPressTicks = longPressTicks
        self.tickTime = tickTime
        #init gpio
        GPIO.setup(self.gpioPin, GPIO.IN)
        
    def get(self):
        return GPIO.input(self.gpioPin)

    def pressed(self):
        #Returns a boolean representing whether the button is pressed
        buttonPressed = False
        # if gpio input is equal to the pressed state
        if GPIO.input(self.gpioPin) == self.pressedState: buttonPressed = True
        return buttonPressed

    def run(self):
        #start the button control
        self.running = True
        self.lastPressedState = self.ButtonPressStates.NOTPRESSED

        # if the button is pressed when the class starts, wait till it is released
        while self.pressed(): time.sleep(self.tickTime)

        # while the control is running
        while self.running:
            # wait for the button to be pressed
            while self.pressed() == False and self.running:
                time.sleep(self.tickTime)

            ticks = 0
            # wait for the button to be released
            while self.pressed() == True and self.running:
                ticks += 1
                time.sleep(self.tickTime)

            #was it press a short or long time    
            if ticks > self.shortPressTicks and ticks < self.longPressTicks:
                self.lastPressedState = self.ButtonPressStates.SHORTPRESS
            if ticks > self.longPressTicks:
                self.lastPressedState = self.ButtonPressStates.LONGPRESS

            #wait in between button presses
            time.sleep(0.5)

    def checkLastPressedState(self):
        #gets the last pressed state but doesnt reset it
        return self.lastPressedState
    
    def getLastPressedState(self):
        #gets the last pressed state and resets it
        theLastPressedState = self.lastPressedState
        self.lastPressedState = self.ButtonPressStates.NOTPRESSED
        return theLastPressedState

    def stopController(self):
        self.running = False

if __name__ == "__main__":

    try:

        #set gpio mode
        GPIO.setmode(GPIO.BCM)

        #create button
        button = ButtonControl(22, 0, BUTTONSHORTPRESSTICKS, BUTTONLONGPRESSTICKS, BUTTONTICKTIME)
        button.start()
        print "Button - started controller"

        time.sleep(1)

        #while the button hasnt received a long press, keep on looping
        while(button.checkLastPressedState() != button.ButtonPressStates.LONGPRESS):
            
            if (button.checkLastPressedState() == button.ButtonPressStates.SHORTPRESS):

                button.getLastPressedState()

                print "short button press"
                
            #wait for a bit
            time.sleep(0.1)
        
    except KeyboardInterrupt:
        print "User Cancelled (Ctrl C)"
        
    except:
        print "Unexpected error - ", sys.exc_info()[0], sys.exc_info()[1]
        raise
    
    finally:
        #stop button
        button.stopController()
        button.join()
        print "Button - Stopped controller"
        #cleanup gpio
        GPIO.cleanup()
        print "Stopped"
