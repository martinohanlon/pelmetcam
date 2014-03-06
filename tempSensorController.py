import threading
import time

DEVICESDIR = "/sys/bus/w1/devices/"

#class for holding temperature values
class Temperature():
    def __init__(self, rawData):
        self.rawData = rawData
    @property
    def C(self):
        return float(self.rawData) / 1000
    @property
    def F(self):
        return self.C * 9.0 / 5.0 + 32.0

#class for controlling the temperature sensor
class TempSensorController(threading.Thread):
    def __init__(self, sensorId, timeToSleep):
        threading.Thread.__init__(self)
        
        #persist the file location
        self.tempSensorFile = DEVICESDIR + sensorId + "/w1_slave"

        #persist properties
        self.sensorId = sensorId
        self.timeToSleep = timeToSleep

	#update the temperature
        self.updateTemp()
        
        #set to not running
        self.running = False
        
    def run(self):
        #loop until its set to stopped
        self.running = True
        while(self.running):
            #update temperature
            self.updateTemp()
            #sleep
            time.sleep(self.timeToSleep)
        self.running = False
        
    def stopController(self):
        self.running = False

    def readFile(self):
        sensorFile = open(self.tempSensorFile, "r")
        lines = sensorFile.readlines()
        sensorFile.close()
        return lines

    def updateTemp(self):
        data = self.readFile()
        #the output from the tempsensor looks like this
        #f6 01 4b 46 7f ff 0a 10 eb : crc=eb YES
        #f6 01 4b 46 7f ff 0a 10 eb t=31375
        #has a YES been returned?
        if data[0].strip()[-3:] == "YES":
            #can I find a temperature (t=)
            equals_pos = data[1].find("t=")
            if equals_pos != -1:
                tempData = data[1][equals_pos+2:]
                #update temperature
                self.temperature = Temperature(tempData)
                #update success status
                self.updateSuccess = True
            else:
                self.updateSuccess = False
        else:
            self.updateSuccess = False
        
if __name__ == "__main__":

    #create temp sensor controller, put your controller Id here
    # look in "/sys/bus/w1/devices/" after running
    #  sudo modprobe w1-gpio
    #  sudo modprobe w1-therm
    tempcontrol = TempSensorController("28-000003aaea41", 1)

    try:
        print("Starting temp sensor controller")
        #start up temp sensor controller
        tempcontrol.start()
        #loop forever, wait for Ctrl C
        while(True):
            print tempcontrol.temperature.C 
            print tempcontrol.temperature.F 
            time.sleep(5)
    #Ctrl C
    except KeyboardInterrupt:
        print "Cancelled"
    
    #Error
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise

    #if it finishes or Ctrl C, shut it down
    finally: 
        print "Stopping temp sensor controller"
        #stop the controller
        tempcontrol.stopController()
        #wait for the tread to finish if it hasn't already
        tempcontrol.join()
        
    print "Done"
