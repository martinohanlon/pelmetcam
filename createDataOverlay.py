#Pelmetcam - Create data overlay using data file
from PIL import Image, ImageFont, ImageDraw
from GPSController import *
import time
import datetime
import os
import argparse

DATAFRAME_WIDTH = 250
DATAFRAME_HEIGHT = 800
MAP_POSLEFT = 5
MAP_POSTOP = 5
MAP_WIDTH = 240
MAP_HEIGHT = 240
MAX_SCALE = 1
FONT_PATH = "/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf"
FONT_SIZE = 38

TEXTCOLOUR = "black"
BACKGROUNDCOLOUR = "white"
LINECOLOUR = "black"
STARTDOTCOLOUR = "red"
ENDDOTCOLOUR = "green"
BOXCOLOUR = "#c0c0c0"

def drawPoint(imagedraw,x,y,width,colour):
    imagedraw.ellipse((x-(width/2),y-(width/2),x+(width/2),y+(width/2)), colour)

def drawBoxedText(imagedraw,x,y,width,height,text,textFont,textColour,BoxColour):
    #draw box
    imagedraw.rectangle((x,y,x+width,y+height), outline=BoxColour, fill=BoxColour)
    #get size of text
    textWidth,textHeight = imagedraw.textsize(text, font=textFont)
    #draw text, putting the text in the middle of the box
    imagedraw.text((x+5,y+((height-textHeight)/2)),text,font=textFont, fill=textColour)
    

class DataDrawer():
    def __init__(self, imagesFolder):
        #setup variables
        self.imagesFolder = imagesFolder
        self.minX = 99999999999
        self.maxX = -99999999999
        self.minY = 99999999999
        self.maxY = -99999999999
        self.lastFrameNo = 0
        self.lastLat = 0
        self.lastLon = 0
        self.xyPositions = []
        self.mapScale = 1
        self.padX = 0
        self.padY = 0
        #load font
        self.font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        #create first frame
        self.newDataFrame(1,0,"",0,0,0,0,0,0,0)
        
        
    def newDataFrame(self, frameNo, mode, date, lat, lon, altitude, speed, track, climb, tempC):
        #check to make sure the frame has moved on since last time
        if frameNo > self.lastFrameNo:
            
            #create sumbolic links between last frame and this frame
            for missingFrameNo in range(self.lastFrameNo+1, frameNo): 
                os.symlink(self.imagesFolder + "/" + "{0:06d}".format(self.lastFrameNo) + ".jpg",
                           self.imagesFolder + "/" + "{0:06d}".format(missingFrameNo) + ".jpg")

            #create new image
            frame = Image.new("RGBA", (DATAFRAME_WIDTH, DATAFRAME_HEIGHT), BACKGROUNDCOLOUR)
            frameDraw = ImageDraw.Draw(frame)

            #data
            #drawBoxedText(frameDraw,10,590,230,20,"Time      " + date[:16],self.font,TEXTCOLOUR,BOXCOLOUR)
            #drawBoxedText(frameDraw,10,620,230,20,"Temp      " + str(round(tempC,1)) + " C",self.font,TEXTCOLOUR,BOXCOLOUR)
            #drawBoxedText(frameDraw,10,650,230,20,"Speed     " + str(round(speed * GpsUtils.MPS_TO_MPH,1)) + " mph",self.font,TEXTCOLOUR,BOXCOLOUR)
            #drawBoxedText(frameDraw,10,680,230,20,"Altitude  " + str(round(altitude,1)) + " m",self.font,TEXTCOLOUR,BOXCOLOUR)
            #drawBoxedText(frameDraw,10,710,230,20,"Climb     " + str(round(climb,1)),self.font,TEXTCOLOUR,BOXCOLOUR)
            #drawBoxedText(frameDraw,10,450,230,20,"Track     " + str(round(track,1)),self.font,TEXTCOLOUR,BOXCOLOUR)
            #drawBoxedText(frameDraw,10,740,230,20,"Latitude  " + str(lat),self.font,TEXTCOLOUR,BOXCOLOUR)
            #drawBoxedText(frameDraw,10,770,230,20,"Longitude " + str(lon),self.font,TEXTCOLOUR,BOXCOLOUR)
            if mode==1: drawBoxedText(frameDraw,10,250,230,20,"No GPS Fix",self.font,TEXTCOLOUR,BOXCOLOUR)
            drawBoxedText(frameDraw,10,660,230,60,str(round(speed * GpsUtils.MPS_TO_MPH,1)) + " mph",self.font,TEXTCOLOUR,BOXCOLOUR)
            drawBoxedText(frameDraw,10,730,230,60,str(round(altitude,1)) + " m",self.font,TEXTCOLOUR,BOXCOLOUR)

            
            #map
            #only create map if we have a GPS fix
            if lat != "nan" and lon != "nan":
                #only add a new set of coords if the lat and lon have changed
                if self.lastLat != lat or self.lastLon != lon:
                    #get x & y coords
                    x,y = GpsUtils.latLongToXY(lat, lon)

                    #add x,y to list
                    self.xyPositions.append([x,y])
                
                    #update mins and maxs
                    if x < self.minX: self.minX = x
                    if x > self.maxX: self.maxX = x
                    if y < self.minY: self.minY = y
                    if y > self.maxY: self.maxY = y

                    #persist lat and lon
                    self.lastLat = lat
                    self.lastLon = lon
                
                    #calculate scale
                    diffX = self.maxX - self.minX
                    #print "diffX " + str(diffX)
                    diffY = self.maxY - self.minY
                    #print "diffY " + str(diffY)
                    if diffX > diffY: 
                        if diffX != 0: self.mapScale = MAP_WIDTH / float(diffX)
                        else: self.mapScale = 1
                    else: 
                        if diffY != 0: self.mapScale = MAP_HEIGHT / float(diffY)
                        else: self.mapScale = 1
                
                    #print "mapScale " + str(self.mapScale)

                    #set max scale
                    if self.mapScale > MAX_SCALE: self.mapScale = MAX_SCALE 
                
                    #re-calculate padding
                    self.padX = int((MAP_WIDTH - (diffX * self.mapScale)) / 2)
                    self.padY = int((MAP_HEIGHT - (diffY * self.mapScale)) / 2)

                #draw map box
                frameDraw.rectangle((MAP_POSLEFT, MAP_POSTOP, MAP_POSLEFT + MAP_WIDTH, MAP_POSTOP + MAP_HEIGHT), outline=BOXCOLOUR, fill=BOXCOLOUR)
                #frameDraw.rectangle((0,250,50,300), outline="red", fill="red")

                #draw lines
                #print len(self.xyPositions)
                for position in range(1, len(self.xyPositions)):
                    #print self.xyPositions[position-1]
                    #print self.xyPositions[position]
                    #draw line between previous position and this one
                    x1 = MAP_POSLEFT + self.padX + abs((self.xyPositions[position-1][0] * self.mapScale) - (self.minX * self.mapScale))
                    y1 = MAP_POSTOP + self.padY + abs((self.xyPositions[position-1][1] * self.mapScale) - (self.maxY * self.mapScale))
                    x2 = MAP_POSLEFT + self.padX + abs((self.xyPositions[position][0] * self.mapScale) - (self.minX * self.mapScale))
                    y2 = MAP_POSTOP + self.padY + abs((self.xyPositions[position][1] * self.mapScale) - (self.maxY * self.mapScale))
                    #print "coords - " + str(x1) + " " + str(y1) + " " + str(x2) + " " + str(y2)
                    frameDraw.line((x1, y1, x2, y2), fill=LINECOLOUR, width=3)

                #draw start and end point
                if len(self.xyPositions) > 1:
                    # start
                    drawPoint(frameDraw, MAP_POSLEFT + self.padX + abs((self.xyPositions[0][0] * self.mapScale) - (self.minX * self.mapScale)), MAP_POSTOP + self.padY + abs((self.xyPositions[0][1] * self.mapScale) - (self.maxY * self.mapScale)), 10, STARTDOTCOLOUR)
                    # end
                    drawPoint(frameDraw, MAP_POSLEFT + self.padX + abs((self.xyPositions[len(self.xyPositions)-1][0] * self.mapScale) - (self.minX * self.mapScale)), MAP_POSTOP + self.padY + abs((self.xyPositions[len(self.xyPositions)-1][1] * self.mapScale) - (self.maxY * self.mapScale)), 10, ENDDOTCOLOUR)
            #save image
            #frame.save(self.imagesFolder + "/" + "{0:06d}".format(frameNo) + ".png", "PNG")
            frame.save(self.imagesFolder + "/" + "{0:06d}".format(frameNo) + ".jpg", "JPEG", quality=100)
            #frame.save(self.imagesFolder + "/" + "{0:06d}".format(frameNo) + ".gif", "GIF")
            #update last frame
            self.lastFrameNo = frameNo
            
if __name__ == "__main__":

    #Command line options
    parser = argparse.ArgumentParser(description="Pelmetcam - Create data overlay")
    parser.add_argument("path", help="The location of the data directory")
    args = parser.parse_args()

    #open data file
    datafile = open(args.path + "/data.csv", "r")

    #create data drawer class
    datadrawer = DataDrawer(args.path)

    count=0

    #for each line 
    for line in datafile:
        resultstring = line
        dataitems = line.split(",")
        #create frame
        # newDataFrame(self, frameNo, mode, date, lat, lon, altitude speed, track, climb, tempC)
        datadrawer.newDataFrame(int(dataitems[0]),
                                int(dataitems[1]),
                                dataitems[2],
                                float(dataitems[4]),
                                float(dataitems[5]),
                                float(dataitems[6]),
                                float(dataitems[7]),
                                float(dataitems[8]),
                                float(dataitems[9]),
                                float(dataitems[10]))
        #debug only do first 500
        #count += 1
        #if count==500: break

    datafile.close()

